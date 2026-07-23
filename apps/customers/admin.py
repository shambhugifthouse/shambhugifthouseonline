from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'total_purchases', 'outstanding_balance', 'created_at')
    search_fields = ('name', 'phone', 'email')
