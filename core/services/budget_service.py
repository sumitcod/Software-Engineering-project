"""
Business Logic Layer: Budget Service
This module handles all budget-related business logic including spending calculations and alerts.
"""
from decimal import Decimal
from django.db.models import Sum, Q
from core.models import Budget, Transaction, Category
from datetime import date
from django.utils import timezone


class BudgetService:
    """
    Service class for budget-related business operations.
    Implements the business logic layer for budget tracking and alerts.
    """
    
    @staticmethod
    def get_budget_status(budget):
        """
        Calculate the current status of a budget including spent amount and percentage.
        
        Args:
            budget: Budget instance
            
        Returns:
            dict: Dictionary containing:
                - spent: Decimal amount spent
                - remaining: Decimal amount remaining
                - percentage: Float percentage of budget used (0-100)
                - status: String status ('good', 'warning', 'danger')
        """
        # Calculate spent amount for this budget's category within the period
        spent = Transaction.objects.filter(
            user=budget.user,
            category=budget.category,
            type=Transaction.EXPENSE,
            date__gte=budget.period_start,
            date__lte=budget.period_end
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Calculate remaining amount
        remaining = budget.amount - spent
        
        # Calculate percentage
        if budget.amount > 0:
            percentage = float((spent / budget.amount) * 100)
        else:
            percentage = 0.0
        
        # Determine status based on percentage
        if percentage < 70:
            status = 'good'
        elif percentage < 90:
            status = 'warning'
        else:
            status = 'danger'
        
        return {
            'spent': spent,
            'remaining': remaining,
            'percentage': percentage,
            'status': status,
            'is_exceeded': spent > budget.amount
        }
    
    @staticmethod
    def get_all_budgets_with_status(user):
        """
        Get all budgets for a user with their current status.
        
        Args:
            user: User instance
            
        Returns:
            list: List of dictionaries, each containing budget and its status
        """
        budgets = Budget.objects.filter(user=user).select_related('category')
        
        budget_data = []
        for budget in budgets:
            status = BudgetService.get_budget_status(budget)
            budget_data.append({
                'budget': budget,
                'spent': status['spent'],
                'remaining': status['remaining'],
                'percentage': status['percentage'],
                'status': status['status'],
                'is_exceeded': status['is_exceeded']
            })
        
        return budget_data
    
    @staticmethod
    def get_active_budgets(user):
        """
        Get currently active budgets (where current date is within period).
        
        Args:
            user: User instance
            
        Returns:
            QuerySet: Active budget queryset
        """
        today = date.today()
        return Budget.objects.filter(
            user=user,
            period_start__lte=today,
            period_end__gte=today
        ).select_related('category')
    
    @staticmethod
    def check_budget_alerts(user, transaction=None):
        """
        Check for budget alerts and return warning messages.
        
        Args:
            user: User instance
            transaction: Optional transaction to check against budgets
            
        Returns:
            list: List of alert messages (strings)
        """
        alerts = []
        
        # Get active budgets
        active_budgets = BudgetService.get_active_budgets(user)
        
        for budget in active_budgets:
            status = BudgetService.get_budget_status(budget)
            
            # If transaction is provided, check if it affects this budget
            if transaction:
                if transaction.category == budget.category and transaction.type == Transaction.EXPENSE:
                    # This transaction affects this budget
                    if status['is_exceeded']:
                        alerts.append(
                            f"⚠️ Budget Exceeded: You've exceeded your '{budget.category.name}' "
                            f"budget by ${abs(status['remaining']):.2f}!"
                        )
                    elif status['percentage'] >= 90:
                        alerts.append(
                            f"⚠️ Budget Alert: You've used {status['percentage']:.1f}% of your "
                            f"'{budget.category.name}' budget. Only ${status['remaining']:.2f} remaining!"
                        )
            else:
                # General check without specific transaction
                if status['is_exceeded']:
                    alerts.append(
                        f"Budget '{budget.category.name}' is exceeded by ${abs(status['remaining']):.2f}"
                    )
                elif status['percentage'] >= 90:
                    alerts.append(
                        f"Budget '{budget.category.name}' is at {status['percentage']:.1f}% "
                        f"(${status['remaining']:.2f} remaining)"
                    )
        
        return alerts
    
    @staticmethod
    def get_budget_summary(user):
        """
        Get a summary of all active budgets for dashboard display.
        
        Args:
            user: User instance
            
        Returns:
            dict: Summary containing total budgets, exceeded count, and warning count
        """
        active_budgets = BudgetService.get_active_budgets(user)
        
        total_count = active_budgets.count()
        exceeded_count = 0
        warning_count = 0
        
        for budget in active_budgets:
            status = BudgetService.get_budget_status(budget)
            if status['is_exceeded']:
                exceeded_count += 1
            elif status['percentage'] >= 90:
                warning_count += 1
        
        return {
            'total': total_count,
            'exceeded': exceeded_count,
            'warning': warning_count,
            'good': total_count - exceeded_count - warning_count
        }
    
    @staticmethod
    def create_monthly_budget(user, category, amount):
        """
        Create a budget for the current month.
        
        Args:
            user: User instance
            category: Category instance
            amount: Decimal budget amount
            
        Returns:
            Budget: Created budget instance
        """
        today = date.today()
        
        # Calculate first and last day of current month
        from calendar import monthrange
        _, last_day = monthrange(today.year, today.month)
        
        period_start = date(today.year, today.month, 1)
        period_end = date(today.year, today.month, last_day)
        
        budget = Budget.objects.create(
            user=user,
            category=category,
            amount=amount,
            period_start=period_start,
            period_end=period_end
        )
        
        return budget
    
    @staticmethod
    def validate_budget_overlap(user, category, period_start, period_end, exclude_budget_id=None):
        """
        Check if a budget for the same category overlaps with existing budgets.
        
        Args:
            user: User instance
            category: Category instance
            period_start: Start date of new budget
            period_end: End date of new budget
            exclude_budget_id: Optional budget ID to exclude from check (for updates)
            
        Returns:
            bool: True if overlap exists, False otherwise
        """
        overlapping = Budget.objects.filter(
            user=user,
            category=category
        ).filter(
            Q(period_start__lte=period_end) & Q(period_end__gte=period_start)
        )
        
        if exclude_budget_id:
            overlapping = overlapping.exclude(id=exclude_budget_id)
        
        return overlapping.exists()
