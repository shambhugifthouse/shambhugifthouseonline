from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'barcode', 'name', 'category', 'selling_price', 'cost_price', 'stock_quantity', 'is_active')
    list_filter = ('category', 'is_active', 'gst_percent')
    search_fields = ('name', 'sku', 'barcode')
    list_editable = ('selling_price', 'stock_quantity')
