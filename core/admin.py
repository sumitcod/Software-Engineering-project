"""
Admin configuration for FinGuard models.
Registers models with the Django admin interface for easy management.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Account, Category, Transaction, Budget


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for User model.
    """
    list_display = ['username', 'email', 'phone', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'phone']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone',)}),
    )


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """
    Admin for Account model.
    """
    list_display = ['user', 'name', 'balance', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('user', 'name', 'balance')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin for Category model.
    """
    list_display = ['name', 'type', 'user', 'is_default', 'created_at']
    list_filter = ['type', 'is_default', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'type', 'user', 'is_default')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Show all categories including default ones.
        """
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin for Transaction model.
    """
    list_display = ['user', 'type', 'category', 'amount', 'date', 'created_at']
    list_filter = ['type', 'date', 'category', 'created_at']
    search_fields = ['user__username', 'description', 'category__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('user', 'account', 'type', 'category', 'amount', 'date')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Optimize queries with select_related.
        """
        qs = super().get_queryset(request)
        return qs.select_related('user', 'account', 'category')


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    """
    Admin for Budget model.
    """
    list_display = ['user', 'category', 'amount', 'period_start', 'period_end', 'created_at']
    list_filter = ['period_start', 'period_end', 'created_at']
    search_fields = ['user__username', 'category__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'period_start'
    
    fieldsets = (
        ('Budget Information', {
            'fields': ('user', 'category', 'amount')
        }),
        ('Period', {
            'fields': ('period_start', 'period_end')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Optimize queries with select_related.
        """
        qs = super().get_queryset(request)
        return qs.select_related('user', 'category')


# Customize admin site header
admin.site.site_header = 'FinGuard Administration'
admin.site.site_title = 'FinGuard Admin'
admin.site.index_title = 'Welcome to FinGuard Administration'
