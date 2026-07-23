from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal
from .models import Customer
from apps.authentication.models import log_action

@login_required
def customer_list_view(request):
    search_query = request.GET.get('q', '').strip()
    customers = Customer.objects.all()

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
                log_action(request.user, "Add Customer", "Customers", f"Created customer: {cust.name}", request)
                messages.success(request, f"Customer '{cust.name}' added successfully.")
            return redirect('customers:list')

        elif action == 'pay_khata':
            cust_id = request.POST.get('customer_id')
            cust = get_object_or_404(Customer, id=cust_id)
            amount = Decimal(request.POST.get('amount', '0.00'))
            if amount > 0:
                cust.outstanding_balance = max(Decimal('0.00'), cust.outstanding_balance - amount)
                cust.save()
                log_action(request.user, "Clear Customer Khata", "Customers", f"Customer {cust.name} paid ₹{amount}", request)
                messages.success(request, f"Payment of ₹{amount} recorded for {cust.name}. Remaining Khata balance: ₹{cust.outstanding_balance}")
            return redirect('customers:list')

    context = {
        'customers': customers,
        'search_query': search_query,
    }
    return render(request, 'customers.html', context)
