"""
Domain Layer: Models for FinGuard application
This module contains all database models following the domain-driven design pattern.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds phone field for additional user information.
    """
    phone = models.CharField(max_length=15, blank=True, null=True, help_text="Contact phone number")
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username


class Account(models.Model):
    """
    Account model representing a user's financial account.
    Each user has one default "Main Account" created automatically.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100, default='Main Account')
    balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Current account balance calculated from transactions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts'
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class Category(models.Model):
    """
    Category model for transaction classification.
    Includes predefined system categories and user-created custom categories.
    """
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'
    
    TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]
    
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='categories',
        null=True,
        blank=True,
        help_text="Null for system categories, set for user-created categories"
    )
    is_default = models.BooleanField(
        default=False,
        help_text="True for system-wide default categories"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['type', 'name']
        unique_together = [['name', 'user', 'type']]
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Transaction(models.Model):
    """
    Transaction model for recording income and expense entries.
    Automatically updates account balance on save/delete through signals.
    """
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'
    
    TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='transactions')
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Transaction amount (always positive)"
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True, help_text="Optional transaction notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['-date', '-created_at']),
            models.Index(fields=['user', 'type']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.amount} - {self.category.name}"
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure category type matches transaction type.
        """
        if self.category.type != self.type:
            raise ValueError(f"Category type must match transaction type. Expected {self.type}, got {self.category.type}")
        super().save(*args, **kwargs)


class Budget(models.Model):
    """
    Budget model for tracking spending limits per category.
    Tracks monthly budgets with period start/end dates.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Budget limit amount"
    )
    period_start = models.DateField(help_text="Budget period start date")
    period_end = models.DateField(help_text="Budget period end date")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'budgets'
        verbose_name = 'Budget'
        verbose_name_plural = 'Budgets'
        ordering = ['-period_start']
        indexes = [
            models.Index(fields=['user', 'period_start', 'period_end']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.category.name} - {self.amount} ({self.period_start} to {self.period_end})"
    
    def clean(self):
        """
        Validate that period_end is after period_start.
        """
        from django.core.exceptions import ValidationError
        if self.period_end <= self.period_start:
            raise ValidationError('Period end date must be after period start date.')
    
    def save(self, *args, **kwargs):
        """
        Call full_clean before saving to ensure validation.
        """
        self.full_clean()
        super().save(*args, **kwargs)
