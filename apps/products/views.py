import csv
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from .models import Product, Category
from apps.services.models import ServiceItem

def public_store_view(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True).select_related('category')
    try:
        services = ServiceItem.objects.filter(is_active=True)
    except Exception:
        services = []

    search_query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(sku__icontains=search_query) | 
            Q(barcode__icontains=search_query)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    context = {
        'products': products,
        'categories': categories,
        'services': services,
        'search_query': search_query,
        'category_id': category_id,
    }
    return render(request, 'shop_home.html', context)


@login_required
def product_list_view(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True).select_related('category')

    # Search & Filters
    search_query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    low_stock = request.GET.get('low_stock', '')
    view_mode = request.GET.get('view', 'table')

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(sku__icontains=search_query) | 
            Q(barcode__icontains=search_query)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    if low_stock == 'true':
        products = [p for p in products if p.is_low_stock]

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            sku = request.POST.get('sku', '').strip()
            barcode = request.POST.get('barcode', '').strip() or None
            
            if Product.objects.filter(sku=sku).exists():
                messages.error(request, f"Product SKU '{sku}' already exists.")
                return redirect('products:list')

            if barcode and Product.objects.filter(barcode=barcode).exists():
                messages.error(request, f"Product Barcode '{barcode}' already exists.")
                return redirect('products:list')

            category_obj = Category.objects.filter(id=request.POST.get('category')).first()
            
            product = Product.objects.create(
                name=request.POST.get('name', '').strip(),
                category=category_obj,
                sku=sku,
                barcode=barcode,
                cost_price=Decimal(request.POST.get('cost_price', '0.00')),
                mrp=Decimal(request.POST.get('mrp', '0.00')),
                selling_price=Decimal(request.POST.get('selling_price', '0.00')),
                gst_percent=Decimal(request.POST.get('gst_percent', '18.00')),
                stock_quantity=int(request.POST.get('stock_quantity', '0')),
                min_stock_level=int(request.POST.get('min_stock_level', '5')),
                unit=request.POST.get('unit', 'Pcs'),
                expiry_date=request.POST.get('expiry_date') or None
            )

            if 'image' in request.FILES:
                product.image = request.FILES['image']
                product.save()

            log_action(request.user, "Add Product", "Products", f"Created product: {product.name} ({product.sku})", request)
            messages.success(request, f"Product '{product.name}' added successfully!")
            return redirect('products:list')

        elif action == 'edit':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)

            category_obj = Category.objects.filter(id=request.POST.get('category')).first()
            product.name = request.POST.get('name', '').strip()
            product.category = category_obj
            product.cost_price = Decimal(request.POST.get('cost_price', '0.00'))
            product.mrp = Decimal(request.POST.get('mrp', '0.00'))
            product.selling_price = Decimal(request.POST.get('selling_price', '0.00'))
            product.gst_percent = Decimal(request.POST.get('gst_percent', '18.00'))
            product.stock_quantity = int(request.POST.get('stock_quantity', '0'))
            product.min_stock_level = int(request.POST.get('min_stock_level', '5'))
            product.unit = request.POST.get('unit', 'Pcs')
            product.expiry_date = request.POST.get('expiry_date') or None

            if 'image' in request.FILES:
                product.image = request.FILES['image']

            product.save()
            log_action(request.user, "Edit Product", "Products", f"Updated product: {product.name}", request)
            messages.success(request, f"Product '{product.name}' updated successfully!")
            return redirect('products:list')

        elif action == 'delete':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            product.is_active = False
            product.save()
            log_action(request.user, "Delete Product", "Products", f"Deactivated product: {product.name}", request)
            messages.warning(request, f"Product '{product.name}' deleted.")
            return redirect('products:list')

    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_id': category_id,
        'low_stock': low_stock,
        'view_mode': view_mode
    }
    return render(request, 'products.html', context)


@login_required
def category_list_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        icon = request.POST.get('icon', 'fa-box').strip()
        description = request.POST.get('description', '').strip()
        category_id = request.POST.get('category_id')

        if category_id:
            category = get_object_or_404(Category, id=category_id)
            category.name = name
            category.icon = icon
            category.description = description
            category.save()
            messages.success(request, f"Category '{name}' updated.")
        else:
            if Category.objects.filter(name=name).exists():
                messages.error(request, f"Category '{name}' already exists.")
            else:
                Category.objects.create(name=name, icon=icon, description=description)
                messages.success(request, f"Category '{name}' created.")
    return redirect('products:list')


@login_required
def export_products_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Shambhu_Products_Catalog.csv"'

    writer = csv.writer(response)
    writer.writerow(['SKU', 'Barcode', 'Product Name', 'Category', 'Cost Price (₹)', 'MRP (₹)', 'Selling Price (₹)', 'Margin (%)', 'GST %', 'Stock Qty', 'Unit', 'Expiry Date'])

    products = Product.objects.filter(is_active=True).select_related('category')
    for p in products:
        writer.writerow([
            p.sku,
            p.barcode or '',
            p.name,
            p.category.name if p.category else 'Uncategorized',
            p.cost_price,
            p.mrp,
            p.selling_price,
            p.profit_margin_percent,
            p.gst_percent,
            p.stock_quantity,
            p.unit,
            p.expiry_date.strftime('%Y-%m-%d') if p.expiry_date else ''
        ])
    return response


@login_required
def product_search_api(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    
    products = Product.objects.filter(is_active=True)
    
    if category_id:
        products = products.filter(category_id=category_id)
        
    if query:
        products = products.filter(
            Q(barcode__iexact=query) |
            Q(sku__iexact=query) |
            Q(name__icontains=query) |
            Q(barcode__icontains=query)
        )

    results = []
    for p in products[:30]:
        results.append({
            'id': p.id,
            'name': p.name,
            'sku': p.sku,
            'barcode': p.barcode or '',
            'mrp': float(p.mrp),
            'selling_price': float(p.selling_price),
            'gst_percent': float(p.gst_percent),
            'stock_quantity': p.stock_quantity,
            'unit': p.unit,
            'category': p.category.name if p.category else 'General',
            'is_low_stock': p.is_low_stock,
            'image_url': p.image.url if p.image else None
        })

    return JsonResponse({'status': 'success', 'products': results})
