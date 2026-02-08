"""
Business Logic Layer: Transaction Service
This module handles all transaction-related business logic including balance calculations.
"""
from decimal import Decimal
from django.db.models import Sum, Q
from core.models import Transaction, Account
from datetime import date


class TransactionService:
    """
    Service class for transaction-related business operations.
    Implements the business logic layer for transactions and account balance management.
    """
    
    @staticmethod
    def recalculate_account_balance(account):
        """
        Recalculate account balance based on all transactions.
        
        Args:
            account: Account instance to recalculate
            
        Returns:
            Decimal: The new calculated balance
        """
        # Calculate total income
        total_income = Transaction.objects.filter(
            account=account,
            type=Transaction.INCOME
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Calculate total expenses
        total_expense = Transaction.objects.filter(
            account=account,
            type=Transaction.EXPENSE
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Calculate net balance
        new_balance = total_income - total_expense
        
        # Update account balance
        account.balance = new_balance
        account.save(update_fields=['balance', 'updated_at'])
        
        return new_balance
    
    @staticmethod
    def get_user_total_balance(user):
        """
        Get total balance across all user accounts.
        
        Args:
            user: User instance
            
        Returns:
            Decimal: Total balance across all accounts
        """
        total = Account.objects.filter(user=user).aggregate(
            total=Sum('balance')
        )['total'] or Decimal('0.00')
        
        return total
    
    @staticmethod
    def get_filtered_transactions(user, filters=None):
        """
        Get filtered transactions for a user.
        
        Args:
            user: User instance
            filters: Dictionary containing filter parameters
                - start_date: Filter transactions from this date
                - end_date: Filter transactions until this date
                - category: Filter by category ID
                - type: Filter by transaction type (INCOME/EXPENSE)
                
        Returns:
            QuerySet: Filtered transaction queryset
        """
        queryset = Transaction.objects.filter(user=user)
        
        if filters:
            if filters.get('start_date'):
                queryset = queryset.filter(date__gte=filters['start_date'])
            
            if filters.get('end_date'):
                queryset = queryset.filter(date__lte=filters['end_date'])
            
            if filters.get('category'):
                queryset = queryset.filter(category_id=filters['category'])
            
            if filters.get('type'):
                queryset = queryset.filter(type=filters['type'])
        
        return queryset.select_related('category', 'account').order_by('-date', '-created_at')
    
    @staticmethod
    def get_monthly_summary(user, month=None, year=None):
        """
        Get monthly income and expense summary for a user.
        
        Args:
            user: User instance
            month: Month number (1-12), defaults to current month
            year: Year, defaults to current year
            
        Returns:
            dict: Summary containing total_income, total_expense, net
        """
        if not month:
            month = date.today().month
        if not year:
            year = date.today().year
        
        # Filter transactions for the specified month
        transactions = Transaction.objects.filter(
            user=user,
            date__year=year,
            date__month=month
        )
        
        # Calculate totals
        total_income = transactions.filter(
            type=Transaction.INCOME
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        total_expense = transactions.filter(
            type=Transaction.EXPENSE
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        net = total_income - total_expense
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'net': net,
            'month': month,
            'year': year
        }
    
    @staticmethod
    def get_expenses_by_category(user, month=None, year=None):
        """
        Get expense breakdown by category for chart visualization.
        
        Args:
            user: User instance
            month: Month number (1-12), defaults to current month
            year: Year, defaults to current year
            
        Returns:
            dict: Dictionary with category names as keys and amounts as values
        """
        if not month:
            month = date.today().month
        if not year:
            year = date.today().year
        
        # Get expense transactions for the month grouped by category
        expenses = Transaction.objects.filter(
            user=user,
            type=Transaction.EXPENSE,
            date__year=year,
            date__month=month
        ).values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        # Convert to dictionary
        result = {item['category__name']: float(item['total']) for item in expenses}
        
        return result
    
    @staticmethod
    def create_transaction(user, account, transaction_data):
        """
        Create a new transaction and update account balance.
        
        Args:
            user: User instance
            account: Account instance
            transaction_data: Dictionary with transaction fields
            
        Returns:
            Transaction: Created transaction instance
        """
        transaction = Transaction.objects.create(
            user=user,
            account=account,
            **transaction_data
        )
        
        # Balance will be updated automatically via signal
        return transaction
    
    @staticmethod
    def update_transaction(transaction, transaction_data):
        """
        Update an existing transaction.
        
        Args:
            transaction: Transaction instance to update
            transaction_data: Dictionary with updated transaction fields
            
        Returns:
            Transaction: Updated transaction instance
        """
        for field, value in transaction_data.items():
            setattr(transaction, field, value)
        
        transaction.save()
        
        # Balance will be updated automatically via signal
        return transaction
    
    @staticmethod
    def delete_transaction(transaction):
        """
        Delete a transaction.
        
        Args:
            transaction: Transaction instance to delete
        """
        account = transaction.account
        transaction.delete()
        
        # Balance will be updated automatically via signal
