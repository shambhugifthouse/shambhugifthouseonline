from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product

class StockAdjustment(models.Model):
    ADJUSTMENT_TYPES = (
        ('ADD', 'Add Stock / Received'),
        ('REMOVE', 'Damage / Expiry / Loss'),
        ('CORRECTION', 'Audit Correction'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_adjustments')
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    quantity = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    adjusted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.adjustment_type} - {self.product.name} ({self.quantity})"


class StockSpending(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_spendings')
    quantity = models.IntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"₹{self.total_amount} spent on {self.product.name} ({self.quantity} pcs)"

