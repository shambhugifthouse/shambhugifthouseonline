from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import ServiceItem, PrinterConsumable
from apps.authentication.models import log_action

@login_required
def service_list_view(request):
    services = ServiceItem.objects.filter(is_active=True)
    consumables = PrinterConsumable.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        
        # --- Service Rates Actions ---
        if action == 'add':
            service = ServiceItem.objects.create(
                name=request.POST.get('name', '').strip(),
                category=request.POST.get('category', 'XEROX'),
                unit_name=request.POST.get('unit_name', 'Per Page').strip(),
                price=Decimal(request.POST.get('price', '2.00')),
                description=request.POST.get('description', '').strip() or None
            )
            log_action(request.user, "Add Service Rate", "Services", f"Created service item: {service.name} (₹{service.price}/{service.unit_name})", request)
            messages.success(request, f"Service rate for '{service.name}' added successfully.")
            return redirect('services:list')

        elif action == 'edit':
            service_id = request.POST.get('service_id')
            service = get_object_or_404(ServiceItem, id=service_id)
            
            old_price = service.price
            service.name = request.POST.get('name', '').strip()
            service.category = request.POST.get('category', service.category)
            service.unit_name = request.POST.get('unit_name', 'Per Page').strip()
            service.price = Decimal(request.POST.get('price', str(old_price)))
            service.description = request.POST.get('description', '').strip() or None
            service.save()

            log_action(request.user, "Adjust Service Rate", "Services", f"Updated rate for '{service.name}': ₹{old_price} -> ₹{service.price}", request)
            messages.success(request, f"Rate for '{service.name}' updated to ₹{service.price} / {service.unit_name}.")
            return redirect('services:list')

        elif action == 'delete':
            service_id = request.POST.get('service_id')
            service = get_object_or_404(ServiceItem, id=service_id)
            service.is_active = False
            service.save()
            log_action(request.user, "Delete Service Rate", "Services", f"Deactivated service: {service.name}", request)
            messages.warning(request, f"Service '{service.name}' deactivated.")
            return redirect('services:list')

        # --- Printer Consumables (Paper & Ink) Actions ---
        elif action == 'add_consumable':
            name = request.POST.get('name', '').strip()
            item_type = request.POST.get('item_type', 'PAPER')
            brand_or_model = request.POST.get('brand_or_model', '').strip()
            stock_quantity = Decimal(request.POST.get('stock_quantity', '0.00'))
            unit = request.POST.get('unit', 'Rim').strip()
            min_stock_alert = Decimal(request.POST.get('min_stock_alert', '2.00'))
            cost_price = Decimal(request.POST.get('cost_price', '0.00'))
            notes = request.POST.get('notes', '').strip()

            item = PrinterConsumable.objects.create(
                name=name,
                item_type=item_type,
                brand_or_model=brand_or_model,
                stock_quantity=stock_quantity,
                unit=unit,
                min_stock_alert=min_stock_alert,
                cost_price=cost_price,
                notes=notes
            )
            log_action(request.user, "Add Consumable", "Services", f"Added printer consumable: {item.name} ({item.stock_quantity} {item.unit})", request)
            messages.success(request, f"Printer consumable '{item.name}' added to inventory.")
            return redirect('services:list')

        elif action == 'adjust_stock':
            item_id = request.POST.get('item_id')
            item = get_object_or_404(PrinterConsumable, id=item_id)
            adjustment_type = request.POST.get('adjustment_type', 'ADD')
            qty = Decimal(request.POST.get('quantity', '1.00'))

            old_qty = item.stock_quantity
            if adjustment_type == 'ADD':
                item.stock_quantity += qty
                msg = f"Added {qty} {item.unit} to {item.name}. New Stock: {item.stock_quantity} {item.unit}"
            else:
                item.stock_quantity = max(Decimal('0.00'), item.stock_quantity - qty)
                msg = f"Used {qty} {item.unit} of {item.name}. Remaining Stock: {item.stock_quantity} {item.unit}"

            item.save()
            log_action(request.user, "Adjust Consumable Stock", "Services", f"{item.name} stock changed: {old_qty} -> {item.stock_quantity}", request)
            messages.success(request, msg)
            return redirect('services:list')

        elif action == 'delete_consumable':
            item_id = request.POST.get('item_id')
            item = get_object_or_404(PrinterConsumable, id=item_id)
            name = item.name
            item.delete()
            log_action(request.user, "Delete Consumable", "Services", f"Deleted consumable: {name}", request)
            messages.warning(request, f"Consumable '{name}' removed from inventory.")
            return redirect('services:list')

    # Summary calculations for header metrics
    papers_count = consumables.filter(item_type='PAPER').count()
    inks_count = consumables.filter(item_type='INK').count()
    low_stock_count = sum(1 for c in consumables if c.is_low_stock)

    context = {
        'services': services,
        'consumables': consumables,
        'papers_count': papers_count,
        'inks_count': inks_count,
        'low_stock_count': low_stock_count,
    }
    return render(request, 'services.html', context)
