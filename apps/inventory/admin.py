from django.contrib import admin
from .models import StockAdjustment

@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('product', 'adjustment_type', 'quantity', 'reason', 'adjusted_by', 'created_at')
    list_filter = ('adjustment_type', 'created_at')
    search_fields = ('product__name', 'reason')
