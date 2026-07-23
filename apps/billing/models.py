from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from apps.products.models import Product
from apps.customers.models import Customer

class Invoice(models.Model):
    PAYMENT_MODES = (
        ('CASH', 'Cash'),
        ('UPI', 'UPI / QR Code'),
        ('CARD', 'Debit / Credit Card'),
        ('KHATA', 'Customer Khata (Credit)'),
        ('SPLIT', 'Split Payment'),
    )

    PAYMENT_STATUS = (
        ('PAID', 'Fully Paid'),
        ('PARTIAL', 'Partially Paid'),
        ('UNPAID', 'Unpaid (Khata)'),
    )

    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    customer_name = models.CharField(max_length=150, default='Walk-in Customer')
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODES, default='CASH')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PAID')
    notes = models.TextField(blank=True, null=True)
    
    billed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice_number} - ₹{self.grand_total} ({self.customer_name})"


class InvoiceItem(models.Model):
    ITEM_TYPES = (
        ('PRODUCT', 'Product Sale'),
        ('SERVICE', 'Custom Service / Xerox / Printing'),
    )

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, default='PRODUCT')
    
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
