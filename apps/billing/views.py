import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Invoice, InvoiceItem
from apps.products.models import Product, Category
from apps.customers.models import Customer
from apps.authentication.models import log_action

@login_required
def billing_pos_view(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True).select_related('category')
    customers = Customer.objects.all()
    recent_invoices = Invoice.objects.select_related('billed_by')[:10]

    context = {
        'categories': categories,
        'products': products,
        'customers': customers,
        'recent_invoices': recent_invoices,
    }
    return render(request, 'billing.html', context)


@login_required
def process_checkout_api(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

    try:
        data = json.loads(request.body)
        items_data = data.get('items', [])
        if not items_data:
            return JsonResponse({'status': 'error', 'message': 'Cart is empty'}, status=400)

        cust_phone = data.get('customer_phone', '').strip()
        cust_name = data.get('customer_name', '').strip() or 'Walk-in Customer'
        payment_mode = data.get('payment_mode', 'CASH')
        discount_amount = Decimal(str(data.get('discount_amount', 0)))

        customer_obj = None
        if cust_phone:
            customer_obj, _ = Customer.objects.get_or_create(
                phone=cust_phone,
                defaults={'name': cust_name}
            )

        # Generate unique invoice number
        today_str = timezone.now().strftime('%Y%m%d')
        invoice_count = Invoice.objects.filter(created_at__date=timezone.now().date()).count() + 1
        inv_number = f"SGH-{today_str}-{invoice_count:04d}"

        subtotal = Decimal('0.00')
        gst_total = Decimal('0.00')
        
        # Build invoice
        invoice = Invoice.objects.create(
            invoice_number=inv_number,
            customer=customer_obj,
            customer_name=cust_name,
            customer_phone=cust_phone or None,
            payment_mode=payment_mode,
            payment_status='UNPAID' if payment_mode == 'KHATA' else 'PAID',
            billed_by=request.user
        )

        for item in items_data:
            p_id = item.get('id')
            p_name = item.get('name', 'Custom Item')
            qty = int(item.get('quantity', 1))
            unit_price = Decimal(str(item.get('price', 0)))
            gst_pct = Decimal(str(item.get('gst_percent', 0)))
            item_type = item.get('item_type', 'PRODUCT')

            item_subtotal = unit_price * qty
            item_gst = (item_subtotal * gst_pct) / Decimal('100.00')
            item_total = item_subtotal + item_gst

            subtotal += item_subtotal
            gst_total += item_gst

            product_obj = None
            if p_id and item_type == 'PRODUCT':
                product_obj = Product.objects.filter(id=p_id).first()
                if product_obj:
                    product_obj.stock_quantity = max(0, product_obj.stock_quantity - qty)
                    product_obj.save()

            InvoiceItem.objects.create(
                invoice=invoice,
                product=product_obj,
                product_name=p_name,
                item_type=item_type,
                unit_price=unit_price,
                quantity=qty,
                gst_percent=gst_pct,
                total_amount=item_total
            )

        grand_total = max(Decimal('0.00'), subtotal + gst_total - discount_amount)
        invoice.subtotal = subtotal
        invoice.gst_amount = gst_total
        invoice.discount_amount = discount_amount
        invoice.grand_total = grand_total
        invoice.save()

        # Update customer stats if Khata / Customer
        if customer_obj:
            customer_obj.total_purchases += grand_total
            if payment_mode == 'KHATA':
                customer_obj.outstanding_balance += grand_total
            customer_obj.save()

        log_action(request.user, "Checkout POS Invoice", "Billing", f"Created Invoice #{inv_number} for ₹{grand_total}", request)
        return JsonResponse({
            'status': 'success',
            'invoice_id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'grand_total': float(grand_total)
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def invoice_detail_view(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'invoice_detail.html', {'invoice': invoice})


@login_required
def invoice_print_view(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'invoice_print.html', {'invoice': invoice})
