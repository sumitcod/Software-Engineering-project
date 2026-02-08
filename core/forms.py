"""
Presentation Layer: Forms for user input validation and rendering.
This module contains all Django forms using django-bootstrap5 for styling.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User, Transaction, Budget, Category
from decimal import Decimal
from datetime import date


class UserRegistrationForm(UserCreationForm):
    """
    Registration form for new users.
    Extends Django's UserCreationForm with additional fields.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    phone = forms.CharField(
        required=False,
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone (optional)'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})


class UserLoginForm(AuthenticationForm):
    """
    Custom login form with Bootstrap styling.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class TransactionForm(forms.ModelForm):
    """
    Form for creating and editing transactions.
    Dynamically filters categories based on transaction type.
    """
    class Meta:
        model = Transaction
        fields = ['type', 'category', 'amount', 'date', 'description']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set default date to today
        if not self.instance.pk:
            self.fields['date'].initial = date.today()
        
        # Filter categories based on user and transaction type
        if self.user:
            if self.instance and self.instance.pk:
                # For existing transactions, filter by the transaction's type
                transaction_type = self.instance.type
                self.fields['category'].queryset = Category.objects.filter(
                    type=transaction_type
                ).filter(
                    models.Q(user=self.user) | models.Q(is_default=True)
                )
            else:
                # For new transactions, show all categories (will be filtered via JavaScript)
                self.fields['category'].queryset = Category.objects.filter(
                    models.Q(user=self.user) | models.Q(is_default=True)
                ).order_by('type', 'name')
    
    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('type')
        category = cleaned_data.get('category')
        
        # Validate that category type matches transaction type
        if transaction_type and category:
            if category.type != transaction_type:
                raise ValidationError({
                    'category': f'Please select a {transaction_type.lower()} category.'
                })
        
        return cleaned_data


class BudgetForm(forms.ModelForm):
    """
    Form for creating and editing budgets.
    Only allows budgets for expense categories.
    """
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'period_start', 'period_end']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'period_start': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'period_end': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only show expense categories (budgets are for expenses only)
        if self.user:
            from django.db import models as django_models
            self.fields['category'].queryset = Category.objects.filter(
                type=Category.EXPENSE
            ).filter(
                django_models.Q(user=self.user) | django_models.Q(is_default=True)
            ).order_by('name')
    
    def clean(self):
        cleaned_data = super().clean()
        period_start = cleaned_data.get('period_start')
        period_end = cleaned_data.get('period_end')
        
        # Validate that period_end is after period_start
        if period_start and period_end:
            if period_end <= period_start:
                raise ValidationError({
                    'period_end': 'End date must be after start date.'
                })
        
        return cleaned_data


class CategoryForm(forms.ModelForm):
    """
    Form for creating custom categories.
    """
    class Meta:
        model = Category
        fields = ['name', 'type']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category name'
            }),
            'type': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class TransactionFilterForm(forms.Form):
    """
    Form for filtering transactions on the transaction list page.
    """
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Start Date'
        })
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'End Date'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="All Categories"
    )
    type = forms.ChoiceField(
        choices=[('', 'All Types')] + Transaction.TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter categories for the current user
        if user:
            from django.db import models as django_models
            self.fields['category'].queryset = Category.objects.filter(
                django_models.Q(user=user) | django_models.Q(is_default=True)
            ).order_by('type', 'name')


# Import models after defining forms to avoid circular imports
from django.db import models
