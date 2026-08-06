from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from decimal import Decimal
from apps.products.models import Product, Category
from apps.inventory.models import StockSpending
from apps.billing.models import Invoice, InvoiceItem
from apps.customers.models import Customer
from apps.authentication.models import AuditLog

@login_required
def dashboard_view(request):
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'product_handover':
            product_id = request.POST.get('product_id')
            customer_name = request.POST.get('customer_name', '').strip() or 'Walk-in Customer'
            customer_phone = request.POST.get('customer_phone', '').strip()
            quantity = int(request.POST.get('quantity', 1))
            total_amount = Decimal(request.POST.get('amount', '0.00'))
            payment_mode = request.POST.get('payment_mode', 'CASH')
            
            product = get_object_or_404(Product, id=product_id)

            # Reduce stock quantity
            if product.stock_quantity is not None:
                product.stock_quantity = max(0, product.stock_quantity - quantity)
                product.save()

            # Generate unique invoice number: INV-YYMMDD-XXXX
            import random
            now = timezone.now()
            inv_number = f"INV-{now.strftime('%y%m%d')}-{random.randint(1000, 9999)}"

            # If Khata payment mode, record credit in Khata Book
            khata_cust = None
            if payment_mode == 'KHATA':
                from apps.customers.models import record_khata_credit
                khata_identifier = f"{customer_name} ({customer_phone})" if customer_phone else customer_name
                khata_cust = record_khata_credit(
                    customer_info=khata_identifier,
                    amount=total_amount,
                    description=f"Product Handover: {product.name} (x{quantity})",
                    user=request.user
                )

            inv = Invoice.objects.create(
                invoice_number=inv_number,
                customer=khata_cust,
                customer_name=customer_name,
                customer_phone=customer_phone or None,
                subtotal=total_amount,
                discount_amount=Decimal('0.00'),
                gst_amount=Decimal('0.00'),
                grand_total=total_amount,
                payment_mode=payment_mode,
                payment_status='UNPAID' if payment_mode == 'KHATA' else 'PAID',
                notes=f"Dashboard Quick Handover: {product.name} x{quantity}",
                billed_by=request.user
            )

            InvoiceItem.objects.create(
                invoice=inv,
                product=product,
                product_name=product.name,
                item_type='PRODUCT',
                unit_price=(total_amount / Decimal(str(quantity))) if quantity > 0 else total_amount,
                quantity=quantity,
                total_amount=total_amount
            )

            AuditLog.objects.create(
                user=request.user,
                action="Product Handover",
                module="Billing",
                details=f"Handed over {quantity}x {product.name} to {customer_name} for ₹{total_amount} ({payment_mode})"
            )
            
            messages.success(request, f"Product handover recorded! Given {quantity}x '{product.name}' to {customer_name} for ₹{total_amount} ({payment_mode}).")
            return redirect('dashboard:dashboard')

    today = timezone.now().date()
    start_of_month = today.replace(day=1)

    today_invoices = Invoice.objects.filter(created_at__date=today)
    today_revenue = today_invoices.aggregate(total=Sum('grand_total'))['total'] or Decimal('0.00')
    today_sales_count = today_invoices.count()

    monthly_invoices = Invoice.objects.filter(created_at__date__gte=start_of_month)
    monthly_revenue = monthly_invoices.aggregate(total=Sum('grand_total'))['total'] or Decimal('0.00')

    from django.db.models import F
    total_products = Product.objects.filter(is_active=True).count()
    low_stock_qs = Product.objects.filter(is_active=True, stock_quantity__lte=F('min_stock_level'))
    low_stock_count = low_stock_qs.count()
    low_stock_items = list(low_stock_qs[:10])

    all_products = Product.objects.filter(is_active=True).order_by('name')
    recent_invoices = Invoice.objects.select_related('billed_by')[:8]
    recent_logs = AuditLog.objects.select_related('user')[:8]
    total_khata = Customer.objects.aggregate(total=Sum('outstanding_balance'))['total'] or Decimal('0.00')

    total_stock_spending = StockSpending.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    recent_stock_spendings = StockSpending.objects.select_related('product', 'added_by')[:5]

    context = {
        'today_revenue': today_revenue,
        'today_sales_count': today_sales_count,
        'monthly_revenue': monthly_revenue,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'low_stock_items': low_stock_items,
        'all_products': all_products,
        'total_khata': total_khata,
        'total_stock_spending': total_stock_spending,
        'recent_stock_spendings': recent_stock_spendings,
        'recent_invoices': recent_invoices,
        'recent_logs': recent_logs,
    }
    return render(request, 'dashboard.html', context)


@login_required
def reports_view(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    invoices = Invoice.objects.all()
    if start_date:
        invoices = invoices.filter(created_at__date__gte=start_date)
    if end_date:
        invoices = invoices.filter(created_at__date__lte=end_date)

    total_sales = invoices.aggregate(total=Sum('grand_total'))['total'] or Decimal('0.00')
    total_gst = invoices.aggregate(total=Sum('gst_amount'))['total'] or Decimal('0.00')
    total_discount = invoices.aggregate(total=Sum('discount_amount'))['total'] or Decimal('0.00')

    cash_sales = invoices.filter(payment_mode='CASH').aggregate(total=Sum('grand_total'))['total'] or Decimal('0.00')
    upi_sales = invoices.filter(payment_mode='UPI').aggregate(total=Sum('grand_total'))['total'] or Decimal('0.00')
    khata_sales = invoices.filter(payment_mode='KHATA').aggregate(total=Sum('grand_total'))['total'] or Decimal('0.00')

    context = {
        'invoices': invoices[:50],
        'total_sales': total_sales,
        'total_gst': total_gst,
        'total_discount': total_discount,
        'cash_sales': cash_sales,
        'upi_sales': upi_sales,
        'khata_sales': khata_sales,
        'start_date': start_date or '',
        'end_date': end_date or '',
    }
    return render(request, 'reports.html', context)
