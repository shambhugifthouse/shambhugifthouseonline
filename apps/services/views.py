from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from django.db.models import Sum

from .models import ServiceItem, PrinterConsumable, RechargeProvider, RechargeTransaction
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


@login_required
def recharge_view(request):
    # Ensure default mobile & DTH providers exist
    default_providers = [
        {"name": "Airtel", "code": "AIRTEL", "category": "MOBILE", "balance": Decimal("2000.00"), "logo_color": "#EF4444", "icon_class": "fa-tower-cell"},
        {"name": "Jio", "code": "JIO", "category": "MOBILE", "balance": Decimal("3000.00"), "logo_color": "#1D4ED8", "icon_class": "fa-bolt"},
        {"name": "BSNL", "code": "BSNL", "category": "MOBILE", "balance": Decimal("1500.00"), "logo_color": "#059669", "icon_class": "fa-signal"},
        {"name": "VI", "code": "VI", "category": "MOBILE", "balance": Decimal("1200.00"), "logo_color": "#D97706", "icon_class": "fa-phone"},
        {"name": "Tatasky", "code": "TATASKY", "category": "DTH", "balance": Decimal("2500.00"), "logo_color": "#7C3AED", "icon_class": "fa-tv"},
        {"name": "ALL Other", "code": "DTH_OTHER", "category": "DTH", "balance": Decimal("1800.00"), "logo_color": "#475569", "icon_class": "fa-satellite-dish"},
    ]

    for dp in default_providers:
        RechargeProvider.objects.get_or_create(
            code=dp["code"],
            defaults=dp
        )

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'perform_recharge':
            provider_id = request.POST.get('provider_id')
            customer_number = request.POST.get('customer_number', '').strip()
            amount = Decimal(request.POST.get('amount', '0.00'))
            commission = Decimal(request.POST.get('commission', '0.00'))
            payment_mode = request.POST.get('payment_mode', 'CASH')

            provider = get_object_or_404(RechargeProvider, id=provider_id)

            # Prevent double entries / duplicate submissions within 5 seconds
            from django.utils import timezone
            import datetime
            recent_duplicate = RechargeTransaction.objects.filter(
                provider=provider,
                customer_number=customer_number,
                amount=amount,
                created_at__gte=timezone.now() - datetime.timedelta(seconds=5)
            ).exists()

            if recent_duplicate:
                messages.warning(request, f"Duplicate request blocked! A recharge of ₹{amount} for {customer_number} was just submitted.")
                return redirect('services:recharge')

            # Auto-calculate 3% commission for mobile recharges (or if commission is 0)
            if provider.category == 'MOBILE' or commission == Decimal('0.00'):
                commission = (amount * Decimal('0.03')).quantize(Decimal('0.01'))

            if provider.balance < amount:
                messages.error(request, f"Insufficient balance in {provider.name}! Available balance: ₹{provider.balance}")
            else:
                provider.balance -= amount
                jio_bonus_applied = False

                # JIO AUTO BONUS OFFER: If Jio balance reaches or drops below 2000, add 5000 credit bonus
                if provider.code == 'JIO' and provider.balance <= Decimal('2000.00'):
                    provider.balance += Decimal('5000.00')
                    jio_bonus_applied = True

                provider.save()

                tx = RechargeTransaction.objects.create(
                    provider=provider,
                    customer_number=customer_number,
                    amount=amount,
                    commission=commission,
                    payment_mode=payment_mode,
                    status='SUCCESS',
                    performed_by=request.user
                )

                log_action(request.user, "Perform Recharge", "Recharge", f"Recharged ₹{amount} ({payment_mode}) for {provider.name} ({customer_number})", request)

                if jio_bonus_applied:
                    messages.success(request, f"Recharge of ₹{amount} ({payment_mode}) for Jio ({customer_number}) processed! 🎉 Jio Offer Triggered: +₹5,000 Auto Credit Bonus added to Jio Wallet! New Balance: ₹{provider.balance}")
                else:
                    messages.success(request, f"Recharge of ₹{amount} ({payment_mode}) for {provider.name} ({customer_number}) processed successfully!")
            return redirect('services:recharge')

        elif action == 'update_balance':
            provider_id = request.POST.get('provider_id')
            add_balance = Decimal(request.POST.get('add_balance', '0.00'))
            provider = get_object_or_404(RechargeProvider, id=provider_id)
            
            provider.balance += add_balance
            provider.save()

            log_action(request.user, "Top-Up Provider Balance", "Recharge", f"Added ₹{add_balance} balance to {provider.name}. New Balance: ₹{provider.balance}", request)
            messages.success(request, f"Updated balance for {provider.name}. New Balance: ₹{provider.balance}")
            return redirect('services:recharge')

    mobile_providers = RechargeProvider.objects.filter(category='MOBILE', is_active=True).order_by('id')
    dth_providers = RechargeProvider.objects.filter(category='DTH', is_active=True).order_by('id')

    transactions = RechargeTransaction.objects.select_related('provider', 'performed_by')[:50]
    total_recharge_today = transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    previous_customers = []
    seen_numbers = set()
    for tx in RechargeTransaction.objects.select_related('provider').order_by('-created_at')[:100]:
        if tx.customer_number and tx.customer_number not in seen_numbers:
            seen_numbers.add(tx.customer_number)
            previous_customers.append({
                'number': tx.customer_number,
                'provider_id': tx.provider.id,
                'provider_name': tx.provider.name,
                'provider_code': tx.provider.code,
            })

    context = {
        'mobile_providers': mobile_providers,
        'dth_providers': dth_providers,
        'transactions': transactions,
        'total_recharge_today': total_recharge_today,
        'previous_customers': previous_customers,
    }
    return render(request, 'recharge.html', context)


@login_required
def other_services_view(request):
    from .models import OtherServiceTransaction

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_other_service':
            service_type = request.POST.get('service_type', 'COLLEGE_FORM')
            title_or_biller = request.POST.get('title_or_biller', '').strip()
            customer_info = request.POST.get('customer_info', '').strip()
            transaction_amount = Decimal(request.POST.get('transaction_amount', '0.00'))
            service_charge = Decimal(request.POST.get('service_charge', '0.00'))
            payment_mode = request.POST.get('payment_mode', 'CASH')
            notes = request.POST.get('notes', '').strip() or None

            # Duplicate prevention check (5-second throttle)
            from django.utils import timezone
            import datetime
            recent_duplicate = OtherServiceTransaction.objects.filter(
                service_type=service_type,
                customer_info=customer_info,
                transaction_amount=transaction_amount,
                service_charge=service_charge,
                created_at__gte=timezone.now() - datetime.timedelta(seconds=5)
            ).exists()

            if recent_duplicate:
                messages.warning(request, "Duplicate service entry blocked! Transaction was just submitted.")
                return redirect('services:other_services')

            tx = OtherServiceTransaction.objects.create(
                service_type=service_type,
                title_or_biller=title_or_biller,
                customer_info=customer_info,
                transaction_amount=transaction_amount,
                service_charge=service_charge,
                payment_mode=payment_mode,
                notes=notes,
                performed_by=request.user
            )

            log_action(request.user, "Record Other Service", "Services", f"{tx.get_service_type_display()} for {customer_info} - Charge: ₹{service_charge}", request)
            messages.success(request, f"Recorded {tx.get_service_type_display()} for '{customer_info}' with ₹{service_charge} commission/fee ({payment_mode}).")
            return redirect('services:other_services')

        elif action == 'delete_other_service':
            tx_id = request.POST.get('tx_id')
            tx = get_object_or_404(OtherServiceTransaction, id=tx_id)
            desc = str(tx)
            tx.delete()
            log_action(request.user, "Delete Other Service Entry", "Services", f"Deleted service log: {desc}", request)
            messages.warning(request, "Service transaction record deleted.")
            return redirect('services:other_services')

    qs = OtherServiceTransaction.objects.select_related('performed_by')

    # Summary metrics (on unsliced queryset)
    forms_count = qs.filter(service_type='COLLEGE_FORM').count()
    light_bills_count = qs.filter(service_type='ELECTRICITY_BILL').count()
    withdrawals_count = qs.filter(service_type='CASH_WITHDRAWAL').count()
    total_charges_collected = qs.aggregate(total=Sum('service_charge'))['total'] or Decimal('0.00')

    # Slice for display table
    transactions = qs[:100]

    context = {
        'transactions': transactions,
        'forms_count': forms_count,
        'light_bills_count': light_bills_count,
        'withdrawals_count': withdrawals_count,
        'total_charges_collected': total_charges_collected,
    }
    return render(request, 'other_services.html', context)

