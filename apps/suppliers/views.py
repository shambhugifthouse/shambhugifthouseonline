from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Supplier
from apps.authentication.models import log_action

@login_required
def supplier_list_view(request):
    suppliers = Supplier.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            supplier = Supplier.objects.create(
                name=request.POST.get('name', '').strip(),
                company_name=request.POST.get('company_name', '').strip() or None,
                phone=request.POST.get('phone', '').strip(),
                email=request.POST.get('email', '').strip() or None,
                gstin=request.POST.get('gstin', '').strip() or None,
                address=request.POST.get('address', '').strip() or None,
            )
            log_action(request.user, "Add Supplier", "Suppliers", f"Created supplier: {supplier.name}", request)
            messages.success(request, f"Supplier '{supplier.name}' added successfully.")
            return redirect('suppliers:list')

    context = {
        'suppliers': suppliers
    }
    return render(request, 'suppliers.html', context)
