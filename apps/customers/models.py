from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Customer(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, unique=True, db_index=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    total_purchases = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    outstanding_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Khata / Credit balance owed by customer")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.phone})"


class KhataEntry(models.Model):
    ENTRY_TYPES = (
        ('CREDIT', 'Udhar / Credit Given (+)'),
        ('PAYMENT', 'Jama / Payment Received (-)'),
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='khata_entries')
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES, default='CREDIT')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255, help_text="e.g. College Form Fee, Light Bill, Cash Payment")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.name} - {self.get_entry_type_display()}: ₹{self.amount}"


def record_khata_credit(customer_info, amount, description, user=None):
    """
    Finds or creates a Customer based on phone/name in customer_info,
    adds amount to customer.outstanding_balance, and creates a KhataEntry.
    """
    import re
    if not customer_info or amount <= Decimal('0.00'):
        return None

    info_str = str(customer_info).strip()
    phone_match = re.search(r'\b[6-9]\d{9}\b', info_str)
    if phone_match:
        phone = phone_match.group(0)
        name = info_str.replace(phone, '').strip(' ()-') or f"Customer {phone}"
    else:
        phone = f"CUST-{abs(hash(info_str)) % 1000000:06d}"
        name = info_str

    cust, _ = Customer.objects.get_or_create(
        phone=phone,
        defaults={'name': name, 'outstanding_balance': Decimal('0.00')}
    )
    if not cust.name or cust.name.startswith("Customer CUST-"):
        cust.name = name

    cust.outstanding_balance += Decimal(str(amount))
    cust.save()

    entry = KhataEntry.objects.create(
        customer=cust,
        entry_type='CREDIT',
        amount=Decimal(str(amount)),
        description=description,
        created_by=user
    )
    return cust


