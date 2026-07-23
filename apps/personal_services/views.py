from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
import datetime

from .models import ExpenseCategory, Expense, EMITracker, EMIPayment

def dashboard(request):
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # Expenses query
    expenses = Expense.objects.select_related('category').all()
    
    # Monthly Expenses Sum
    monthly_expenses_sum = Expense.objects.filter(
        expense_date__month=current_month,
        expense_date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    total_expenses_all_time = Expense.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # EMI Trackers
    emis = EMITracker.objects.all()
    active_emis = emis.filter(status='ACTIVE')
    
    # Monthly EMI Commitment Sum
    monthly_emi_commitment = active_emis.aggregate(total=Sum('monthly_emi'))['total'] or Decimal('0.00')
    active_emi_count = active_emis.count()

    # Find next upcoming EMI
    next_emi = None
    upcoming_emis = active_emis.filter(due_day_of_month__gte=today.day).order_by('due_day_of_month')
    if upcoming_emis.exists():
        next_emi = upcoming_emis.first()
    elif active_emis.exists():
        # Wrap around to lowest due day next month
        next_emi = active_emis.order_by('due_day_of_month').first()

    categories = ExpenseCategory.objects.all()

    context = {
        'expenses': expenses[:50],  # Latest 50 expenses
        'emis': emis,
        'categories': categories,
        'monthly_expenses_sum': monthly_expenses_sum,
        'total_expenses_all_time': total_expenses_all_time,
        'monthly_emi_commitment': monthly_emi_commitment,
        'active_emi_count': active_emi_count,
        'next_emi': next_emi,
        'today': today,
    }
    return render(request, 'personal_services.html', context)


def add_expense(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        category_id = request.POST.get('category')
        expense_date = request.POST.get('expense_date') or timezone.now().date()
        payment_method = request.POST.get('payment_method', 'UPI')
        receipt_number = request.POST.get('receipt_number', '')
        notes = request.POST.get('notes', '')

        category = None
        if category_id:
            category = ExpenseCategory.objects.filter(id=category_id).first()

        if title and amount:
            Expense.objects.create(
                title=title,
                amount=Decimal(amount),
                category=category,
                expense_date=expense_date,
                payment_method=payment_method,
                receipt_number=receipt_number,
                notes=notes
            )
            messages.success(request, f"Expense '{title}' recorded successfully!")
        else:
            messages.error(request, "Please enter required expense title and amount.")

    return redirect('personal_services:dashboard')


def delete_expense(request, pk):
    if request.method == 'POST':
        expense = get_object_or_404(Expense, pk=pk)
        title = expense.title
        expense.delete()
        messages.success(request, f"Expense '{title}' deleted.")
    return redirect('personal_services:dashboard')


def add_emi(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        lender_name = request.POST.get('lender_name')
        total_loan_amount = request.POST.get('total_loan_amount') or '0.00'
        monthly_emi = request.POST.get('monthly_emi')
        due_day_of_month = request.POST.get('due_day_of_month', 5)
        start_date = request.POST.get('start_date') or timezone.now().date()
        tenure_months = request.POST.get('tenure_months', 12)
        paid_installments = request.POST.get('paid_installments', 0)
        notes = request.POST.get('notes', '')

        if title and monthly_emi:
            EMITracker.objects.create(
                title=title,
                lender_name=lender_name,
                total_loan_amount=Decimal(total_loan_amount),
                monthly_emi=Decimal(monthly_emi),
                due_day_of_month=int(due_day_of_month),
                start_date=start_date,
                tenure_months=int(tenure_months),
                paid_installments=int(paid_installments),
                notes=notes
            )
            messages.success(request, f"EMI Tracker '{title}' created successfully!")
        else:
            messages.error(request, "Please fill in title and monthly EMI amount.")

    return redirect('personal_services:dashboard')


def delete_emi(request, pk):
    if request.method == 'POST':
        emi = get_object_or_404(EMITracker, pk=pk)
        title = emi.title
        emi.delete()
        messages.success(request, f"EMI Tracker '{title}' deleted.")
    return redirect('personal_services:dashboard')


def pay_emi_installment(request, pk):
    if request.method == 'POST':
        emi = get_object_or_404(EMITracker, pk=pk)
        payment_method = request.POST.get('payment_method', 'BANK')
        transaction_ref = request.POST.get('transaction_ref', '')
        notes = request.POST.get('notes', '')
        log_as_expense = request.POST.get('log_as_expense') == 'on'

        # Increment installment count
        emi.paid_installments += 1
        if emi.paid_installments >= emi.tenure_months:
            emi.status = 'COMPLETED'
        emi.save()

        # Create payment record
        payment = EMIPayment.objects.create(
            emi=emi,
            installment_number=emi.paid_installments,
            amount_paid=emi.monthly_emi,
            payment_date=timezone.now().date(),
            payment_method=payment_method,
            transaction_ref=transaction_ref,
            notes=notes
        )

        # Optionally log as an expense in Expense model
        if log_as_expense:
            category, _ = ExpenseCategory.objects.get_or_create(
                name="EMI & Loan Payment",
                defaults={'icon': 'fa-credit-card', 'color_badge': 'bg-warning'}
            )
            Expense.objects.create(
                title=f"EMI: {emi.title} (Inst #{emi.paid_installments}/{emi.tenure_months})",
                category=category,
                amount=emi.monthly_emi,
                expense_date=timezone.now().date(),
                payment_method=payment_method,
                notes=f"Lender: {emi.lender_name} | Ref: {transaction_ref}",
                receipt_number=transaction_ref
            )

        messages.success(request, f"Recorded installment #{emi.paid_installments} for {emi.title} (₹{emi.monthly_emi})!")

    return redirect('personal_services:dashboard')
