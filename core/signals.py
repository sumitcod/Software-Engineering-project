"""
Signal handlers for automatic operations.
This module handles automatic account balance updates when transactions are created/updated/deleted.
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from .models import User, Account, Transaction


@receiver(post_save, sender=User)
def create_default_account(sender, instance, created, **kwargs):
    """
    Automatically create a default "Main Account" when a new user is created.
    """
    if created:
        Account.objects.create(
            user=instance,
            name='Main Account',
            balance=0
        )


@receiver(post_save, sender=Transaction)
def update_balance_on_transaction_save(sender, instance, created, **kwargs):
    """
    Update account balance when a transaction is created or updated.
    This is triggered after a transaction is saved.
    """
    # Skip if we're already in a transaction update to prevent recursion
    if hasattr(instance, '_updating_balance'):
        return
    
    # Use transaction service to recalculate balance
    from core.services.transaction_service import TransactionService
    TransactionService.recalculate_account_balance(instance.account)


@receiver(post_delete, sender=Transaction)
def update_balance_on_transaction_delete(sender, instance, **kwargs):
    """
    Update account balance when a transaction is deleted.
    """
    from core.services.transaction_service import TransactionService
    TransactionService.recalculate_account_balance(instance.account)
