import csv
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Count, Q

from apps.products.models import Product, Category
from .models import StockAdjustment, StockSpending
from apps.authentication.models import log_action

@login_required
def stock_list_view(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    low_stock_products = [p for p in products if p.is_low_stock]
    adjustments = StockAdjustment.objects.select_related('product', 'adjusted_by')[:50]
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        adj_type = request.POST.get('adjustment_type')
        qty = int(request.POST.get('quantity', '0'))
        reason = request.POST.get('reason', '').strip()

        if product_id and qty > 0:
            product = get_object_or_404(Product, id=product_id)
            if adj_type == 'ADD':
                product.stock_quantity += qty
                total_amt = Decimal(qty) * product.cost_price
                StockSpending.objects.create(
                    product=product,
                    quantity=qty,
                    unit_cost=product.cost_price,
                    total_amount=total_amt,
                    added_by=request.user,
                    note=reason or "Stock Received / Added"
                )
            elif adj_type == 'REMOVE':
                product.stock_quantity = max(0, product.stock_quantity - qty)
            elif adj_type == 'CORRECTION':
                product.stock_quantity = qty

            product.save()
            StockAdjustment.objects.create(
                product=product,
                adjustment_type=adj_type,
                quantity=qty,
                reason=reason,
                adjusted_by=request.user
            )
            log_action(request.user, "Adjust Stock", "Inventory", f"Adjusted stock for {product.name} ({adj_type} {qty})", request)
            messages.success(request, f"Stock updated for '{product.name}'. New quantity: {product.stock_quantity}")
            return redirect('inventory:list')

    context = {
        'products': products,
        'low_stock_products': low_stock_products,
        'adjustments': adjustments,
    }
    return render(request, 'inventory.html', context)


@login_required
def stock_spending_list_view(request):
    spendings = StockSpending.objects.select_related('product', 'product__category', 'added_by').all()
    categories = Category.objects.all()

    search_query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    if search_query:
        spendings = spendings.filter(
            Q(product__name__icontains=search_query) |
            Q(product__sku__icontains=search_query) |
            Q(note__icontains=search_query)
        )

    if category_id:
        spendings = spendings.filter(product__category_id=category_id)

    if start_date:
        spendings = spendings.filter(created_at__date__gte=start_date)

    if end_date:
        spendings = spendings.filter(created_at__date__lte=end_date)

    # Aggregations
    total_spent = spendings.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_units_purchased = spendings.aggregate(total=Sum('quantity'))['total'] or 0
    total_entries_count = spendings.count()

    top_spent_product = spendings.values('product__name').annotate(
        product_total=Sum('total_amount')
    ).order_by('-product_total').first()

    context = {
        'spendings': spendings[:200],
        'categories': categories,
        'search_query': search_query,
        'category_id': category_id,
        'start_date': start_date,
        'end_date': end_date,
        'total_spent': total_spent,
        'total_units_purchased': total_units_purchased,
        'total_entries_count': total_entries_count,
        'top_spent_product': top_spent_product,
    }
    return render(request, 'stock_spending.html', context)


@login_required
def export_spending_csv(request):
    spendings = StockSpending.objects.select_related('product', 'product__category', 'added_by').all()

    search_query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    if search_query:
        spendings = spendings.filter(
            Q(product__name__icontains=search_query) |
            Q(product__sku__icontains=search_query)
        )
    if category_id:
        spendings = spendings.filter(product__category_id=category_id)
    if start_date:
        spendings = spendings.filter(created_at__date__gte=start_date)
    if end_date:
        spendings = spendings.filter(created_at__date__lte=end_date)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Stock_Spending_Log.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date & Time', 'Product Name', 'SKU', 'Category', 'Quantity Added', 'Unit Cost (₹)', 'Total Spent (₹)', 'Added By', 'Note'])

    for s in spendings:
        writer.writerow([
            s.created_at.strftime('%Y-%m-%d %H:%M'),
            s.product.name,
            s.product.sku,
            s.product.category.name if s.product.category else 'Uncategorized',
            s.quantity,
            s.unit_cost,
            s.total_amount,
            s.added_by.username if s.added_by else 'System',
            s.note or ''
        ])

    return response

