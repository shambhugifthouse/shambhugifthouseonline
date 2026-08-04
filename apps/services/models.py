from django.db import models
from django.contrib.auth.models import User
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


class RechargeProvider(models.Model):
    CATEGORY_CHOICES = (
        ('MOBILE', 'Mobile Operator'),
        ('DTH', 'DTH Operator'),
    )

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='MOBILE')
    logo_color = models.CharField(max_length=30, default='#E11D48')
    icon_class = models.CharField(max_length=50, default='fa-mobile-screen-button')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()}) - Balance: ₹{self.balance}"


class RechargeTransaction(models.Model):
    STATUS_CHOICES = (
        ('SUCCESS', 'Success'),
        ('PENDING', 'Pending'),
        ('FAILED', 'Failed'),
    )
    PAYMENT_MODE_CHOICES = (
        ('CASH', 'Cash'),
        ('ONLINE', 'Online / UPI'),
        ('KHATA', 'Customer Khata (Credit)'),
    )

    provider = models.ForeignKey(RechargeProvider, on_delete=models.CASCADE, related_name='transactions')
    customer_number = models.CharField(max_length=30, help_text="Mobile Number or DTH VC / Subscriber ID")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, default='CASH')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUCCESS')
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"₹{self.amount} ({self.get_payment_mode_display()}) - {self.provider.name} ({self.customer_number})"


class OtherServiceTransaction(models.Model):
    SERVICE_TYPE_CHOICES = (
        ('COLLEGE_FORM', 'College / Online Form Submission'),
        ('ELECTRICITY_BILL', 'Electricity / Light Bill Payment'),
        ('CASH_WITHDRAWAL', 'Payment Banks Cash Withdrawal / AEPS'),
        ('MONEY_TRANSFER', 'Money Transfer / DMT'),
    )
    PAYMENT_MODE_CHOICES = (
        ('CASH', 'Cash'),
        ('ONLINE', 'Online / UPI'),
        ('KHATA', 'Customer Khata (Credit)'),
    )

    service_type = models.CharField(max_length=30, choices=SERVICE_TYPE_CHOICES, default='COLLEGE_FORM')
    title_or_biller = models.CharField(max_length=200, help_text="e.g. FY B.Com Admission Form, MSEB Light Bill, Bank Cash Out")
    customer_info = models.CharField(max_length=200, help_text="Customer Name, Mobile No, or Consumer ID")
    transaction_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), help_text="Bill Amount or Cash Withdrawal Amount")
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Accepted Fee / Editable Commission")
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, default='CASH')
    notes = models.TextField(blank=True, null=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_service_type_display()} - {self.customer_info} (Charge: ₹{self.service_charge})"



