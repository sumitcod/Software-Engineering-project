"""
Management command to initialize default categories.
Run: python manage.py init_categories
"""
from django.core.management.base import BaseCommand
from core.models import Category


class Command(BaseCommand):
    help = 'Initialize default categories for FinGuard'
    
    def handle(self, *args, **options):
        """
        Create default income and expense categories.
        """
        # Default expense categories
        expense_categories = [
            'Food',
            'Rent',
            'Transport',
            'Entertainment',
            'Bills',
            'Shopping',
            'Health',
            'Other'
        ]
        
        # Default income categories
        income_categories = [
            'Salary',
            'Freelance',
            'Investment',
            'Gift',
            'Other'
        ]
        
        created_count = 0
        
        # Create expense categories
        for name in expense_categories:
            category, created = Category.objects.get_or_create(
                name=name,
                type=Category.EXPENSE,
                user=None,
                defaults={'is_default': True}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created expense category: {name}')
                )
        
        # Create income categories
        for name in income_categories:
            category, created = Category.objects.get_or_create(
                name=name,
                type=Category.INCOME,
                user=None,
                defaults={'is_default': True}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created income category: {name}')
                )
        
        if created_count == 0:
            self.stdout.write(
                self.style.WARNING('All default categories already exist.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully created {created_count} default categories!')
            )
