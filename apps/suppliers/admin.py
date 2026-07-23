from django.contrib import admin
from .models import Supplier

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_name', 'phone', 'email', 'gstin', 'created_at')
    search_fields = ('name', 'company_name', 'phone')
