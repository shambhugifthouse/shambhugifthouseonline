from django.db import models
from django.utils.text import slugify
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=50, default='fa-box', help_text="FontAwesome icon class name e.g. fa-gift")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    GST_CHOICES = (
        (Decimal('0.00'), '0%'),
        (Decimal('5.00'), '5%'),
        (Decimal('12.00'), '12%'),
        (Decimal('18.00'), '18%'),
        (Decimal('28.00'), '28%'),
    )

    UNIT_CHOICES = (
        ('Pcs', 'Pieces (Pcs)'),
        ('Box', 'Box'),
        ('Pkg', 'Package'),
        ('Sheet', 'Sheet'),
        ('Meter', 'Meter'),
        ('Set', 'Set'),
        ('Pack', 'Pack'),
    )

    name = models.CharField(max_length=200, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True, db_index=True)
    
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    mrp = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, choices=GST_CHOICES, default=Decimal('18.00'))
    
    stock_quantity = models.IntegerField(default=0)
    min_stock_level = models.IntegerField(default=5)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='Pcs')
    expiry_date = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def profit_margin(self):
        return self.selling_price - self.cost_price

    @property
    def profit_margin_percent(self):
        if self.selling_price and self.selling_price > 0:
            return round(((self.selling_price - self.cost_price) / self.selling_price) * 100, 2)
        return 0.0

    @property
    def discount_percent(self):
        if self.mrp and self.mrp > 0 and self.mrp > self.selling_price:
            return round(((self.mrp - self.selling_price) / self.mrp) * 100, 2)
        return 0.0

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.min_stock_level
