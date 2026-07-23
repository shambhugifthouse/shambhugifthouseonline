from django.contrib import admin
from .models import ServiceItem, PrinterConsumable

@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit_name', 'price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')

@admin.register(PrinterConsumable)
class PrinterConsumableAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_type', 'brand_or_model', 'stock_quantity', 'unit', 'min_stock_alert', 'cost_price', 'last_refilled_at')
    list_filter = ('item_type',)
    search_fields = ('name', 'brand_or_model', 'notes')

