from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.products.models import Product, Category
from .models import StockAdjustment
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
