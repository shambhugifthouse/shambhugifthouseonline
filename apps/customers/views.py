from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from decimal import Decimal
from .models import Customer, KhataEntry
from apps.authentication.models import log_action

@login_required
def customer_list_view(request):
    search_query = request.GET.get('q', '').strip()
    customers = Customer.objects.prefetch_related('khata_entries').all()

    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            phone = request.POST.get('phone', '').strip()
            if Customer.objects.filter(phone=phone).exists():
                messages.error(request, f"Customer with phone '{phone}' already exists.")
            else:
                cust = Customer.objects.create(
                    name=request.POST.get('name', '').strip(),
                    phone=phone,
                    email=request.POST.get('email', '').strip() or None,
                    address=request.POST.get('address', '').strip() or None,
                    outstanding_balance=Decimal(request.POST.get('outstanding_balance', '0.00'))
                )
                if cust.outstanding_balance > Decimal('0.00'):
                    KhataEntry.objects.create(
                        customer=cust,
                        entry_type='CREDIT',
                        amount=cust.outstanding_balance,
                        description="Initial Khata Balance Added",
                        created_by=request.user
                    )
                log_action(request.user, "Add Customer", "Customers", f"Created customer: {cust.name}", request)
                messages.success(request, f"Customer '{cust.name}' added successfully.")
            return redirect('customers:list')

        elif action == 'edit_customer':
            cust_id = request.POST.get('customer_id')
            cust = get_object_or_404(Customer, id=cust_id)
            cust.name = request.POST.get('name', cust.name).strip()
            cust.phone = request.POST.get('phone', cust.phone).strip()
            cust.email = request.POST.get('email', '').strip() or None
            cust.address = request.POST.get('address', '').strip() or None
            old_balance = cust.outstanding_balance
            new_balance = Decimal(request.POST.get('outstanding_balance', str(old_balance)))
            cust.outstanding_balance = new_balance
            cust.save()

            if new_balance != old_balance:
                diff = new_balance - old_balance
                KhataEntry.objects.create(
                    customer=cust,
                    entry_type='CREDIT' if diff > 0 else 'PAYMENT',
                    amount=abs(diff),
                    description=f"Manual Balance Adjustment: ₹{old_balance} -> ₹{new_balance}",
                    created_by=request.user
                )

            log_action(request.user, "Edit Customer", "Customers", f"Updated customer {cust.name} (Balance: ₹{new_balance})", request)
            messages.success(request, f"Updated details for customer '{cust.name}'.")
            return redirect('customers:list')

        elif action == 'pay_khata':
            cust_id = request.POST.get('customer_id')
            cust = get_object_or_404(Customer, id=cust_id)
            amount = Decimal(request.POST.get('amount', '0.00'))
            notes = request.POST.get('notes', 'Jama / Payment Received').strip()
            if amount > 0:
                cust.outstanding_balance = max(Decimal('0.00'), cust.outstanding_balance - amount)
                cust.save()
                KhataEntry.objects.create(
                    customer=cust,
                    entry_type='PAYMENT',
                    amount=amount,
                    description=notes,
                    created_by=request.user
                )
                log_action(request.user, "Clear Customer Khata", "Customers", f"Customer {cust.name} paid ₹{amount}", request)
                messages.success(request, f"Payment of ₹{amount} recorded for {cust.name}. Remaining Khata balance: ₹{cust.outstanding_balance}")
            return redirect('customers:list')

        elif action == 'edit_khata_entry':
            entry_id = request.POST.get('entry_id')
            entry = get_object_or_404(KhataEntry, id=entry_id)
            cust = entry.customer
            old_amount = entry.amount
            old_type = entry.entry_type

            new_amount = Decimal(request.POST.get('amount', str(old_amount)))
            new_type = request.POST.get('entry_type', old_type)
            entry.description = request.POST.get('description', entry.description).strip()
            entry.amount = new_amount
            entry.entry_type = new_type
            entry.save()

            # Recalculate customer total outstanding balance dynamically from entries
            credits = KhataEntry.objects.filter(customer=cust, entry_type='CREDIT').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            payments = KhataEntry.objects.filter(customer=cust, entry_type='PAYMENT').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            cust.outstanding_balance = max(Decimal('0.00'), credits - payments)
            cust.save()

            log_action(request.user, "Edit Khata Entry", "Customers", f"Edited Khata entry #{entry.id} for {cust.name}", request)
            messages.success(request, f"Khata transaction updated for {cust.name}.")
            return redirect('customers:list')

        elif action == 'delete_khata_entry':
            entry_id = request.POST.get('entry_id')
            entry = get_object_or_404(KhataEntry, id=entry_id)
            cust = entry.customer
            entry.delete()

            # Recalculate customer balance after entry deletion
            credits = KhataEntry.objects.filter(customer=cust, entry_type='CREDIT').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            payments = KhataEntry.objects.filter(customer=cust, entry_type='PAYMENT').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            cust.outstanding_balance = max(Decimal('0.00'), credits - payments)
            cust.save()

            log_action(request.user, "Delete Khata Entry", "Customers", f"Deleted Khata entry for {cust.name}", request)
            messages.warning(request, f"Khata entry deleted. Updated balance: ₹{cust.outstanding_balance}")
            return redirect('customers:list')

    context = {
        'customers': customers,
        'search_query': search_query,
    }
    return render(request, 'customers.html', context)
