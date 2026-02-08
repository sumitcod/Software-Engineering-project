"""
Presentation Layer: Views
This module contains all view logic using Class-Based Views.
Views communicate with the service layer for business logic.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import (
    TemplateView, CreateView, UpdateView, DeleteView, ListView
)
from django.urls import reverse_lazy
from django.db import models as django_models
from datetime import date

from .models import User, Account, Transaction, Budget, Category
from .forms import (
    UserRegistrationForm, UserLoginForm, TransactionForm, 
    BudgetForm, CategoryForm, TransactionFilterForm
)
from .services.transaction_service import TransactionService
from .services.budget_service import BudgetService


# ============================================================================
# Authentication Views
# ============================================================================

class RegisterView(CreateView):
    """
    User registration view.
    Creates a new user account and automatically logs them in.
    """
    model = User
    form_class = UserRegistrationForm
    template_name = 'core/register.html'
    success_url = reverse_lazy('core:dashboard')
    
    def form_valid(self, form):
        """
        Save the user and log them in automatically.
        """
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f'Welcome to FinGuard, {self.object.username}!')
        return response
    
    def dispatch(self, request, *args, **kwargs):
        """
        Redirect authenticated users to dashboard.
        """
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)


class LoginView(TemplateView):
    """
    User login view using custom login form.
    """
    template_name = 'core/login.html'
    
    def get(self, request, *args, **kwargs):
        """
        Redirect authenticated users to dashboard.
        """
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        
        form = UserLoginForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        """
        Process login form submission.
        """
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect to next URL or dashboard
            next_url = request.GET.get('next', 'core:dashboard')
            return redirect(next_url)
        
        return render(request, self.template_name, {'form': form})


class LogoutView(TemplateView):
    """
    User logout view.
    """
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
        return redirect('core:login')


# ============================================================================
# Dashboard View
# ============================================================================

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard view displaying:
    - Current balance
    - Recent transactions
    - Budget summary
    - Expense chart
    """
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's main account
        account = Account.objects.filter(user=user).first()
        context['account'] = account
        
        # Get current balance
        context['current_balance'] = account.balance if account else 0
        
        # Get recent transactions (last 10)
        context['recent_transactions'] = Transaction.objects.filter(
            user=user
        ).select_related('category').order_by('-date', '-created_at')[:10]
        
        # Get monthly summary
        monthly_summary = TransactionService.get_monthly_summary(user)
        context['monthly_summary'] = monthly_summary
        
        # Get budget summary
        budget_summary = BudgetService.get_budget_summary(user)
        context['budget_summary'] = budget_summary
        
        # Get active budgets with status
        active_budgets = BudgetService.get_active_budgets(user)
        budgets_with_status = []
        for budget in active_budgets[:5]:  # Show top 5 budgets
            status = BudgetService.get_budget_status(budget)
            budgets_with_status.append({
                'budget': budget,
                **status
            })
        context['budgets'] = budgets_with_status
        
        # Get expense data for chart
        expense_data = TransactionService.get_expenses_by_category(user)
        context['expense_chart_labels'] = list(expense_data.keys())
        context['expense_chart_data'] = list(expense_data.values())
        
        # Check for budget alerts
        alerts = BudgetService.check_budget_alerts(user)
        if alerts:
            for alert in alerts:
                messages.warning(self.request, alert)
        
        return context


# ============================================================================
# Transaction Views
# ============================================================================

class TransactionListView(LoginRequiredMixin, ListView):
    """
    List all transactions with filtering options.
    """
    model = Transaction
    template_name = 'core/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20
    
    def get_queryset(self):
        """
        Get filtered transactions based on form inputs.
        """
        filters = {}
        
        # Get filter parameters from GET request
        if self.request.GET.get('start_date'):
            filters['start_date'] = self.request.GET.get('start_date')
        
        if self.request.GET.get('end_date'):
            filters['end_date'] = self.request.GET.get('end_date')
        
        if self.request.GET.get('category'):
            filters['category'] = self.request.GET.get('category')
        
        if self.request.GET.get('type'):
            filters['type'] = self.request.GET.get('type')
        
        return TransactionService.get_filtered_transactions(self.request.user, filters)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TransactionFilterForm(
            data=self.request.GET or None,
            user=self.request.user
        )
        
        # Calculate totals for filtered transactions
        transactions = self.get_queryset()
        total_income = sum(
            t.amount for t in transactions if t.type == Transaction.INCOME
        )
        total_expense = sum(
            t.amount for t in transactions if t.type == Transaction.EXPENSE
        )
        
        context['total_income'] = total_income
        context['total_expense'] = total_expense
        context['net'] = total_income - total_expense
        
        return context


class TransactionCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new transaction.
    """
    model = Transaction
    form_class = TransactionForm
    template_name = 'core/transaction_form.html'
    success_url = reverse_lazy('core:transaction_list')
    
    def get_form_kwargs(self):
        """
        Pass user to form for category filtering.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """
        Set user and account before saving.
        """
        # Get user's main account
        account = Account.objects.filter(user=self.request.user).first()
        if not account:
            messages.error(self.request, 'No account found. Please contact support.')
            return redirect('core:dashboard')
        
        form.instance.user = self.request.user
        form.instance.account = account
        
        response = super().form_valid(form)
        
        messages.success(
            self.request, 
            f'{form.instance.get_type_display()} transaction added successfully!'
        )
        
        # Check for budget alerts
        alerts = BudgetService.check_budget_alerts(self.request.user, form.instance)
        for alert in alerts:
            messages.warning(self.request, alert)
        
        return response


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing transaction.
    """
    model = Transaction
    form_class = TransactionForm
    template_name = 'core/transaction_form.html'
    success_url = reverse_lazy('core:transaction_list')
    
    def get_queryset(self):
        """
        Ensure users can only update their own transactions.
        """
        return Transaction.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        """
        Pass user to form for category filtering.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Transaction updated successfully!')
        return response


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete a transaction.
    """
    model = Transaction
    template_name = 'core/transaction_confirm_delete.html'
    success_url = reverse_lazy('core:transaction_list')
    
    def get_queryset(self):
        """
        Ensure users can only delete their own transactions.
        """
        return Transaction.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Transaction deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# Budget Views
# ============================================================================

class BudgetListView(LoginRequiredMixin, ListView):
    """
    List all budgets with their current status.
    """
    model = Budget
    template_name = 'core/budget_list.html'
    context_object_name = 'budgets'
    
    def get_queryset(self):
        """
        Get user's budgets ordered by period.
        """
        return Budget.objects.filter(
            user=self.request.user
        ).select_related('category').order_by('-period_start')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add status information to each budget
        budgets_with_status = []
        for budget in context['budgets']:
            status = BudgetService.get_budget_status(budget)
            budgets_with_status.append({
                'budget': budget,
                **status
            })
        
        context['budgets_with_status'] = budgets_with_status
        
        return context


class BudgetCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new budget.
    """
    model = Budget
    form_class = BudgetForm
    template_name = 'core/budget_form.html'
    success_url = reverse_lazy('core:budget_list')
    
    def get_form_kwargs(self):
        """
        Pass user to form for category filtering.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """
        Set user before saving and check for overlaps.
        """
        form.instance.user = self.request.user
        
        # Check for overlapping budgets
        if BudgetService.validate_budget_overlap(
            self.request.user,
            form.instance.category,
            form.instance.period_start,
            form.instance.period_end
        ):
            messages.error(
                self.request,
                'A budget for this category already exists for this period.'
            )
            return self.form_invalid(form)
        
        response = super().form_valid(form)
        messages.success(self.request, 'Budget created successfully!')
        return response


class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing budget.
    """
    model = Budget
    form_class = BudgetForm
    template_name = 'core/budget_form.html'
    success_url = reverse_lazy('core:budget_list')
    
    def get_queryset(self):
        """
        Ensure users can only update their own budgets.
        """
        return Budget.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        """
        Pass user to form for category filtering.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """
        Check for overlaps excluding current budget.
        """
        if BudgetService.validate_budget_overlap(
            self.request.user,
            form.instance.category,
            form.instance.period_start,
            form.instance.period_end,
            exclude_budget_id=self.object.id
        ):
            messages.error(
                self.request,
                'A budget for this category already exists for this period.'
            )
            return self.form_invalid(form)
        
        response = super().form_valid(form)
        messages.success(self.request, 'Budget updated successfully!')
        return response


class BudgetDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete a budget.
    """
    model = Budget
    template_name = 'core/budget_confirm_delete.html'
    success_url = reverse_lazy('core:budget_list')
    
    def get_queryset(self):
        """
        Ensure users can only delete their own budgets.
        """
        return Budget.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Budget deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# Category Views
# ============================================================================

class CategoryListView(LoginRequiredMixin, ListView):
    """
    List all categories (default + user-created).
    """
    model = Category
    template_name = 'core/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        """
        Get default categories and user's custom categories.
        """
        return Category.objects.filter(
            django_models.Q(is_default=True) | django_models.Q(user=self.request.user)
        ).order_by('type', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Separate into income and expense categories
        categories = self.get_queryset()
        context['income_categories'] = categories.filter(type=Category.INCOME)
        context['expense_categories'] = categories.filter(type=Category.EXPENSE)
        
        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """
    Create a custom category.
    """
    model = Category
    form_class = CategoryForm
    template_name = 'core/category_form.html'
    success_url = reverse_lazy('core:category_list')
    
    def get_form_kwargs(self):
        """
        Pass user to form.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """
        Set user and ensure it's not a default category.
        """
        form.instance.user = self.request.user
        form.instance.is_default = False
        
        response = super().form_valid(form)
        messages.success(self.request, 'Custom category created successfully!')
        return response
