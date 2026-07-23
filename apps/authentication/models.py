from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'System Admin'),
        ('STAFF', 'Billing Staff'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STAFF')
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    module = models.CharField(max_length=50)
    details = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        username = self.user.username if self.user else "System"
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {username} - {self.action} ({self.module})"


class BusinessProfile(models.Model):
    shop_name = models.CharField(max_length=150, default="SHAMBHU GIFT HOUSE")
    tagline = models.CharField(max_length=200, default="Gifts, Toys, Stationeries, Xerox & Printing Center")
    owner_name = models.CharField(max_length=100, default="Shambhu Nath")
    phone = models.CharField(max_length=20, default="+91 9139090903")
    email = models.EmailField(default="contact@shambhugifthouse.com")
    gstin = models.CharField(max_length=20, default="10AAAAA0000A1Z5")
    address = models.TextField(default="Dhandarphal Bk, Sangamner, Ahilyanagar, 422603")
    receipt_header = models.CharField(max_length=255, default="Thank you for shopping at SHAMBHU GIFT HOUSE!")
    receipt_footer = models.CharField(max_length=255, default="Goods once sold can be exchanged within 7 days. No Cash Refund.")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.shop_name


def log_action(user, action, module, details="", request=None):
    """Utility function to log user actions across the POS system."""
    ip = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
    
    AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action=action,
        module=module,
        details=details,
        ip_address=ip
    )
