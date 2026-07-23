from django.contrib import admin
from .models import ExpenseCategory, Expense, EMITracker, EMIPayment

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color_badge', 'created_at')
    search_fields = ('name',)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'amount', 'expense_date', 'payment_method', 'created_at')
    list_filter = ('category', 'payment_method', 'expense_date')
    search_fields = ('title', 'notes', 'receipt_number')

@admin.register(EMITracker)
class EMITrackerAdmin(admin.ModelAdmin):
    list_display = ('title', 'lender_name', 'monthly_emi', 'due_day_of_month', 'paid_installments', 'tenure_months', 'status')
    list_filter = ('status', 'due_day_of_month')
    search_fields = ('title', 'lender_name')

@admin.register(EMIPayment)
class EMIPaymentAdmin(admin.ModelAdmin):
    list_display = ('emi', 'installment_number', 'amount_paid', 'payment_date', 'payment_method')
    list_filter = ('payment_method', 'payment_date')
