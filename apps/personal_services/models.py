from django.db import models
from django.utils import timezone
from decimal import Decimal

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='fa-receipt', help_text="FontAwesome icon class e.g. fa-receipt")
    color_badge = models.CharField(max_length=50, default='bg-primary', help_text="Bootstrap background badge class")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Expense Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Expense(models.Model):
    PAYMENT_METHODS = (
        ('CASH', 'Cash'),
        ('UPI', 'UPI / GPay / PhonePe'),
        ('BANK', 'Bank Transfer'),
        ('CARD', 'Credit / Debit Card'),
        ('OTHER', 'Other'),
    )

    title = models.CharField(max_length=200)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='UPI')
    notes = models.TextField(blank=True, null=True)
    receipt_number = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expense_date', '-created_at']

    def __str__(self):
        return f"{self.title} - ₹{self.amount} ({self.expense_date})"


class EMITracker(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('PAUSED', 'Paused'),
    )

    title = models.CharField(max_length=200, help_text="e.g. Shop Display Fridge, Laptop EMI")
    lender_name = models.CharField(max_length=150, help_text="e.g. HDFC Bank, Bajaj Finserv, Credit Card")
    total_loan_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    monthly_emi = models.DecimalField(max_digits=10, decimal_places=2)
    due_day_of_month = models.IntegerField(default=5, help_text="Day of month when EMI is due (1 to 31)")
    start_date = models.DateField(default=timezone.now)
    tenure_months = models.IntegerField(default=12, help_text="Total duration in months")
    paid_installments = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "EMI Tracker"
        verbose_name_plural = "EMI Trackers"
        ordering = ['status', 'due_day_of_month', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.lender_name}) - ₹{self.monthly_emi}/mo"

    @property
    def total_paid_amount(self):
        return self.monthly_emi * Decimal(self.paid_installments)

    @property
    def remaining_balance(self):
        rem = self.total_loan_amount - self.total_paid_amount
        return rem if rem > Decimal('0.00') else Decimal('0.00')

    @property
    def remaining_installments(self):
        rem = self.tenure_months - self.paid_installments
        return rem if rem > 0 else 0

    @property
    def progress_percentage(self):
        if self.tenure_months <= 0:
            return 0
        pct = int((self.paid_installments / self.tenure_months) * 100)
        return min(100, max(0, pct))


class EMIPayment(models.Model):
    emi = models.ForeignKey(EMITracker, on_delete=models.CASCADE, related_name='payments')
    installment_number = models.IntegerField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=Expense.PAYMENT_METHODS, default='BANK')
    transaction_ref = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date', '-created_at']

    def __str__(self):
        return f"Installment #{self.installment_number} for {self.emi.title} - ₹{self.amount_paid}"
