"""
Management command to create test/demo data for FinGuard
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
from core.models import User, Account, Category, Transaction, Budget
import random


class Command(BaseCommand):
    help = 'Creates test data for demonstration purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username to create test data for (default: admin)'
        )

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist!'))
            return

        # Get user's account
        account = Account.objects.get(user=user)
        
        # Get categories
        food = Category.objects.get(name='Food', type='EXPENSE')
        rent = Category.objects.get(name='Rent', type='EXPENSE')
        transport = Category.objects.get(name='Transport', type='EXPENSE')
        entertainment = Category.objects.get(name='Entertainment', type='EXPENSE')
        bills = Category.objects.get(name='Bills', type='EXPENSE')
        shopping = Category.objects.get(name='Shopping', type='EXPENSE')
        health = Category.objects.get(name='Health', type='EXPENSE')
        
        salary = Category.objects.get(name='Salary', type='INCOME')
        freelance = Category.objects.get(name='Freelance', type='INCOME')
        investment = Category.objects.get(name='Investment', type='INCOME')
        
        # Delete existing transactions and budgets for this user
        Transaction.objects.filter(user=user).delete()
        Budget.objects.filter(user=user).delete()
        
        self.stdout.write('Creating test data...')
        
        # Create income transactions
        today = timezone.now().date()
        
        # This month's salary
        Transaction.objects.create(
            user=user,
            account=account,
            category=salary,
            type='INCOME',
            amount=Decimal('5000.00'),
            date=today.replace(day=1),
            description='Monthly Salary - February 2026'
        )
        
        # Freelance income
        Transaction.objects.create(
            user=user,
            account=account,
            category=freelance,
            type='INCOME',
            amount=Decimal('1200.00'),
            date=today - timedelta(days=5),
            description='Web Development Project'
        )
        
        # Investment returns
        Transaction.objects.create(
            user=user,
            account=account,
            category=investment,
            type='INCOME',
            amount=Decimal('350.00'),
            date=today - timedelta(days=10),
            description='Stock Dividends'
        )
        
        # Last month's salary
        last_month = today.replace(day=1) - timedelta(days=1)
        Transaction.objects.create(
            user=user,
            account=account,
            category=salary,
            type='INCOME',
            amount=Decimal('5000.00'),
            date=last_month.replace(day=1),
            description='Monthly Salary - January 2026'
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Created income transactions'))
        
        # Create expense transactions for current month
        expenses = [
            (food, Decimal('45.50'), today - timedelta(days=1), 'Grocery Shopping - Walmart'),
            (food, Decimal('28.75'), today - timedelta(days=2), 'Lunch at Restaurant'),
            (food, Decimal('65.20'), today - timedelta(days=4), 'Weekly Groceries'),
            (food, Decimal('15.00'), today - timedelta(days=6), 'Coffee Shop'),
            (food, Decimal('82.30'), today - timedelta(days=8), 'Dinner with Friends'),
            (food, Decimal('120.00'), today - timedelta(days=12), 'Monthly Groceries'),
            
            (transport, Decimal('50.00'), today - timedelta(days=1), 'Gas Station Fill-up'),
            (transport, Decimal('12.50'), today - timedelta(days=3), 'Uber to Downtown'),
            (transport, Decimal('45.00'), today - timedelta(days=7), 'Gas'),
            (transport, Decimal('25.00'), today - timedelta(days=14), 'Parking Fee'),
            
            (entertainment, Decimal('15.99'), today - timedelta(days=2), 'Netflix Subscription'),
            (entertainment, Decimal('45.00'), today - timedelta(days=5), 'Movie Tickets'),
            (entertainment, Decimal('60.00'), today - timedelta(days=9), 'Concert Tickets'),
            (entertainment, Decimal('25.50'), today - timedelta(days=13), 'Video Game'),
            
            (bills, Decimal('120.00'), today.replace(day=5), 'Electric Bill'),
            (bills, Decimal('80.00'), today.replace(day=5), 'Internet Bill'),
            (bills, Decimal('45.00'), today.replace(day=10), 'Phone Bill'),
            
            (shopping, Decimal('89.99'), today - timedelta(days=3), 'New Shoes - Nike'),
            (shopping, Decimal('45.00'), today - timedelta(days=8), 'Clothing Store'),
            (shopping, Decimal('120.00'), today - timedelta(days=11), 'Electronics - Best Buy'),
            
            (health, Decimal('30.00'), today - timedelta(days=6), 'Pharmacy - Prescription'),
            (health, Decimal('85.00'), today - timedelta(days=15), 'Gym Membership'),
            
            (rent, Decimal('1200.00'), today.replace(day=1), 'Monthly Rent Payment'),
        ]
        
        for category, amount, date, description in expenses:
            Transaction.objects.create(
                user=user,
                account=account,
                category=category,
                type='EXPENSE',
                amount=amount,
                date=date,
                description=description
            )
        
        self.stdout.write(self.style.SUCCESS('✓ Created expense transactions'))
        
        # Create some transactions from last month
        last_month_expenses = [
            (food, Decimal('450.00'), last_month.replace(day=15), 'Monthly Groceries'),
            (rent, Decimal('1200.00'), last_month.replace(day=1), 'Monthly Rent'),
            (bills, Decimal('200.00'), last_month.replace(day=5), 'Utilities'),
            (transport, Decimal('180.00'), last_month.replace(day=10), 'Gas - Multiple Fill-ups'),
        ]
        
        for category, amount, date, description in last_month_expenses:
            Transaction.objects.create(
                user=user,
                account=account,
                category=category,
                type='EXPENSE',
                amount=amount,
                date=date,
                description=description
            )
        
        self.stdout.write(self.style.SUCCESS('✓ Created last month transactions'))
        
        # Create budgets for current month
        first_day = today.replace(day=1)
        if today.month == 12:
            last_day = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        budgets = [
            (food, Decimal('500.00')),
            (transport, Decimal('200.00')),
            (entertainment, Decimal('150.00')),
            (shopping, Decimal('300.00')),
            (bills, Decimal('300.00')),
        ]
        
        for category, amount in budgets:
            Budget.objects.create(
                user=user,
                category=category,
                amount=amount,
                period_start=first_day,
                period_end=last_day
            )
        
        self.stdout.write(self.style.SUCCESS('✓ Created budgets'))
        
        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('═' * 50))
        self.stdout.write(self.style.SUCCESS('Test Data Created Successfully!'))
        self.stdout.write(self.style.SUCCESS('═' * 50))
        self.stdout.write('')
        
        # Calculate summary
        current_month_income = Transaction.objects.filter(
            user=user,
            type='INCOME',
            date__year=today.year,
            date__month=today.month
        ).count()
        
        current_month_expenses = Transaction.objects.filter(
            user=user,
            type='EXPENSE',
            date__year=today.year,
            date__month=today.month
        ).count()
        
        total_budgets = Budget.objects.filter(user=user).count()
        
        self.stdout.write(f'📊 Summary:')
        self.stdout.write(f'   • Income Transactions (this month): {current_month_income}')
        self.stdout.write(f'   • Expense Transactions (this month): {current_month_expenses}')
        self.stdout.write(f'   • Active Budgets: {total_budgets}')
        self.stdout.write(f'   • Current Balance: ${account.balance}')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('⚠️  Note: Some budgets may show alerts based on spending!'))
        self.stdout.write('')
        self.stdout.write('🎉 Your dashboard is now populated with realistic data!')
        self.stdout.write('   Visit http://127.0.0.1:8000/dashboard/ to see it in action.')
