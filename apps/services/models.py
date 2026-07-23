from django.db import models
from decimal import Decimal

class ServiceItem(models.Model):
    SERVICE_CATEGORIES = (
        ('XEROX', 'Xerox & Photocopy'),
        ('PRINTING', 'Color & Black/White Printing'),
        ('DTP', 'DTP & Document Typing'),
        ('LAMINATION', 'Lamination'),
        ('PHOTO', 'Passport & Studio Photos'),
        ('ONLINE', 'Online Forms & Government Work'),
        ('BINDING', 'Spiral & Book Binding'),
    )

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=30, choices=SERVICE_CATEGORIES, default='XEROX')
    unit_name = models.CharField(max_length=50, default='Per Page', help_text="e.g. Per Page, Per Photo, Per Copy")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('2.00'))
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} (₹{self.price}/{self.unit_name})"


class PrinterConsumable(models.Model):
    ITEM_TYPES = (
        ('PAPER', 'Paper & Sheets'),
        ('INK', 'Ink & Toner Cartridge'),
        ('OTHER', 'Lamination & Binding Supplies'),
    )

    name = models.CharField(max_length=150)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, default='PAPER')
    brand_or_model = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. JK Copier, Canon IR-2520, Epson L3250")
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    unit = models.CharField(max_length=50, default='Rim', help_text="e.g. Rim, Bottle, Cartridge, Pack, Sheets")
    min_stock_alert = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('2.00'))
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True, null=True)
    last_refilled_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['item_type', 'name']

    def __str__(self):
        return f"{self.name} - {self.stock_quantity} {self.unit}"

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.min_stock_alert

