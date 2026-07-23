from django.contrib import admin
from .models import UserProfile, AuditLog, BusinessProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'module', 'ip_address')
    list_filter = ('module', 'timestamp')
    search_fields = ('action', 'details', 'user__username')
    readonly_fields = ('timestamp', 'user', 'action', 'module', 'details', 'ip_address')

@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'owner_name', 'phone', 'gstin', 'updated_at')
