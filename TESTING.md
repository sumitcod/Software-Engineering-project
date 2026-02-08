# FinGuard - Testing Guide

## Overview

This document provides comprehensive testing procedures for FinGuard application to ensure all features work correctly before deployment.

## Test Environment Setup

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Ensure fresh database
python manage.py migrate
python manage.py init_categories

# Create test superuser
python manage.py createsuperuser
# Username: testadmin
# Password: TestPass123!

# Run server
python manage.py runserver
```

## 1. Authentication Tests

### Test 1.1: User Registration
**Steps:**
1. Navigate to http://127.0.0.1:8000/register/
2. Fill form:
   - Username: testuser1
   - Email: test@example.com
   - Phone: +1234567890
   - Password: SecurePass123!
   - Confirm Password: SecurePass123!
3. Click "Create Account"

**Expected Results:**
- ✓ Redirected to dashboard
- ✓ Welcome message displayed
- ✓ User is logged in automatically
- ✓ Main Account created automatically
- ✓ Balance shows $0.00

**Verification:**
```python
# In Django shell: python manage.py shell
from core.models import User, Account
user = User.objects.get(username='testuser1')
print(user.email)  # Should show test@example.com
print(user.accounts.count())  # Should be 1
print(user.accounts.first().name)  # Should be 'Main Account'
```

### Test 1.2: Login
**Steps:**
1. Logout if logged in
2. Navigate to http://127.0.0.1:8000/login/
3. Enter: testuser1 / SecurePass123!
4. Click "Login"

**Expected Results:**
- ✓ Redirected to dashboard
- ✓ Welcome back message
- ✓ Sidebar shows username

### Test 1.3: Logout
**Steps:**
1. While logged in, click "Logout" in sidebar
2. Confirm logout

**Expected Results:**
- ✓ Redirected to login page
- ✓ Logout confirmation message
- ✓ Cannot access dashboard without login

### Test 1.4: Access Control
**Steps:**
1. Logout
2. Try to access http://127.0.0.1:8000/dashboard/ directly

**Expected Results:**
- ✓ Redirected to login page
- ✓ URL shows next parameter

---

## 2. Transaction Tests

### Test 2.1: Add Income Transaction
**Steps:**
1. Login as testuser1
2. Click "Add Transaction"
3. Fill form:
   - Type: Income
   - Category: Salary (should auto-filter to income categories)
   - Amount: 5000.00
   - Date: Today's date
   - Description: Monthly salary
4. Click "Save Transaction"

**Expected Results:**
- ✓ Redirected to transaction list
- ✓ Success message displayed
- ✓ Transaction appears in list
- ✓ Dashboard balance shows $5000.00
- ✓ Monthly income shows $5000.00

### Test 2.2: Add Expense Transaction
**Steps:**
1. Click "Add Transaction"
2. Fill form:
   - Type: Expense
   - Category: Food
   - Amount: 150.50
   - Date: Today's date
   - Description: Groceries
3. Click "Save Transaction"

**Expected Results:**
- ✓ Transaction saved successfully
- ✓ Dashboard balance shows $4849.50
- ✓ Monthly expense shows $150.50
- ✓ Pie chart displays Food category

### Test 2.3: Edit Transaction
**Steps:**
1. Go to Transactions
2. Click edit icon on the Food transaction
3. Change amount to 200.00
4. Click "Update Transaction"

**Expected Results:**
- ✓ Transaction updated
- ✓ Balance recalculated to $4800.00
- ✓ Success message shown

### Test 2.4: Delete Transaction
**Steps:**
1. Go to Transactions
2. Click delete icon on any transaction
3. Confirm deletion

**Expected Results:**
- ✓ Confirmation page shown
- ✓ Transaction details displayed
- ✓ Warning about balance update
- ✓ After confirmation, transaction removed
- ✓ Balance recalculated correctly

### Test 2.5: Transaction Filtering
**Steps:**
1. Add 5 more transactions (mix of income/expense, different categories)
2. Go to Transactions
3. Test filters:
   - Filter by date range
   - Filter by category
   - Filter by type (Income/Expense)
4. Test pagination (if > 20 transactions)

**Expected Results:**
- ✓ Filters work correctly
- ✓ Summary cards update with filtered data
- ✓ Pagination works
- ✓ Clear filters returns all transactions

### Test 2.6: Category Type Validation
**Steps:**
1. Try to create transaction with:
   - Type: Income
   - Category: Food (expense category)

**Expected Results:**
- ✓ Form validation error
- ✓ Error message about category type mismatch

---

## 3. Budget Tests

### Test 3.1: Create Budget
**Steps:**
1. Login
2. Navigate to Budgets
3. Click "Create Budget"
4. Fill form:
   - Category: Food
   - Amount: 500.00
   - Period Start: First day of current month
   - Period End: Last day of current month
5. Click "Create Budget"

**Expected Results:**
- ✓ Budget created successfully
- ✓ Shows in budget list
- ✓ Progress bar displayed
- ✓ Shows spent amount based on existing transactions
- ✓ Percentage calculated correctly

### Test 3.2: Budget Status Colors
**Steps:**
1. Create budget: Entertainment - $100
2. Add transaction: Entertainment - $50 (50% - should be green)
3. Add transaction: Entertainment - $30 (80% - should be yellow)
4. Add transaction: Entertainment - $30 (110% - should be red)

**Expected Results:**
- ✓ Progress bar color changes:
  - < 70%: Green (On Track)
  - 70-90%: Yellow (Warning)
  - > 90%: Red (Exceeded)
- ✓ Status badge updates accordingly

### Test 3.3: Budget Alerts
**Steps:**
1. Create budget: Transport - $200
2. Add transaction: Transport - $185 (92.5%)

**Expected Results:**
- ✓ Warning alert displayed after transaction creation
- ✓ Alert message shows percentage and remaining amount
- ✓ Alert appears on dashboard if viewed

### Test 3.4: Budget Exceeded Alert
**Steps:**
1. Using above budget, add transaction: Transport - $50

**Expected Results:**
- ✓ Exceeded alert displayed
- ✓ Alert shows over-budget amount
- ✓ Budget card shows red progress bar
- ✓ Remaining amount is negative

### Test 3.5: Edit Budget
**Steps:**
1. Go to Budgets
2. Click dropdown menu on any budget
3. Click "Edit"
4. Change amount to higher value
5. Save

**Expected Results:**
- ✓ Budget updated
- ✓ Percentage recalculated
- ✓ Status may change (red to yellow/green)

### Test 3.6: Delete Budget
**Steps:**
1. Click delete on any budget
2. Confirm deletion

**Expected Results:**
- ✓ Confirmation page shown
- ✓ Budget details displayed
- ✓ Budget deleted successfully
- ✓ Transactions remain intact

### Test 3.7: Budget Period Validation
**Steps:**
1. Try to create budget with:
   - Period Start: 2024-03-01
   - Period End: 2024-02-28 (before start)

**Expected Results:**
- ✓ Form validation error
- ✓ Error message about end date

### Test 3.8: Duplicate Budget Prevention
**Steps:**
1. Create budget: Food - $500 (March 1-31)
2. Try to create another budget: Food - $600 (March 15 - April 15)

**Expected Results:**
- ✓ Validation error
- ✓ Message about overlapping budget

---

## 4. Category Tests

### Test 4.1: View Categories
**Steps:**
1. Navigate to Categories
2. View both income and expense categories

**Expected Results:**
- ✓ Default categories displayed
- ✓ Separated into Income/Expense sections
- ✓ "Default" badge on system categories
- ✓ "Custom" badge on user categories

### Test 4.2: Create Custom Category
**Steps:**
1. Click "Add Custom Category"
2. Fill form:
   - Name: Subscriptions
   - Type: Expense
3. Save

**Expected Results:**
- ✓ Category created
- ✓ Shows in expense categories list
- ✓ Marked as "Custom"
- ✓ Available in transaction/budget forms

### Test 4.3: Use Custom Category
**Steps:**
1. Create transaction using new "Subscriptions" category
2. Verify it works in budgets

**Expected Results:**
- ✓ Custom category appears in dropdowns
- ✓ Works same as default categories

---

## 5. Dashboard Tests

### Test 5.1: Statistics Cards
**Steps:**
1. With transactions created, view dashboard
2. Verify all three stat cards:
   - Current Balance
   - Monthly Income
   - Monthly Expenses

**Expected Results:**
- ✓ Balance = Total Income - Total Expenses
- ✓ Monthly Income = Current month income only
- ✓ Monthly Expenses = Current month expenses only

### Test 5.2: Expense Pie Chart
**Steps:**
1. Ensure multiple expense categories have transactions
2. View dashboard chart

**Expected Results:**
- ✓ Chart displays all expense categories
- ✓ Correct amounts shown in tooltip
- ✓ Legend shows category names
- ✓ Colors are distinct

### Test 5.3: Recent Transactions
**Steps:**
1. View "Recent Transactions" section
2. Verify it shows last 10 transactions

**Expected Results:**
- ✓ Shows up to 10 most recent
- ✓ Sorted by date (newest first)
- ✓ All details displayed correctly
- ✓ "View All" link works

### Test 5.4: Budget Summary Cards
**Steps:**
1. With active budgets, view dashboard
2. Check budget progress bars

**Expected Results:**
- ✓ Shows top 5 active budgets
- ✓ Progress bars colored correctly
- ✓ Spent/Total amounts accurate
- ✓ "View All Budgets" link works

### Test 5.5: Quick Actions
**Steps:**
1. Test "Add Transaction" button from dashboard

**Expected Results:**
- ✓ Button navigates to transaction form
- ✓ Form works correctly

---

## 6. Admin Panel Tests

### Test 6.1: Admin Access
**Steps:**
1. Navigate to http://127.0.0.1:8000/admin/
2. Login with superuser credentials

**Expected Results:**
- ✓ Admin dashboard loads
- ✓ All models listed
- ✓ FinGuard branding displayed

### Test 6.2: Manage Users
**Steps:**
1. In admin, click Users
2. View user list
3. Click on a user
4. Edit phone field
5. Save

**Expected Results:**
- ✓ User list displays all users
- ✓ Can edit user details
- ✓ Changes saved successfully

### Test 6.3: View Transactions
**Steps:**
1. Click Transactions in admin
2. Use filters (type, date, category)
3. Search by description

**Expected Results:**
- ✓ All transactions listed
- ✓ Filters work correctly
- ✓ Search functions properly
- ✓ Can view transaction details

---

## 7. Responsive Design Tests

### Test 7.1: Mobile View
**Steps:**
1. Open browser DevTools (F12)
2. Toggle device toolbar
3. Select iPhone/Android device
4. Navigate through all pages

**Expected Results:**
- ✓ Sidebar collapses/adapts
- ✓ Tables scroll horizontally
- ✓ Charts resize properly
- ✓ Forms remain usable
- ✓ Buttons are touch-friendly

### Test 7.2: Tablet View
**Steps:**
1. Set viewport to iPad
2. Test all pages

**Expected Results:**
- ✓ Layout adapts appropriately
- ✓ 2-column layouts work
- ✓ Navigation remains accessible

---

## 8. Data Integrity Tests

### Test 8.1: Balance Calculation
**Steps:**
1. Note current balance
2. Add income: $1000
3. Add expense: $300
4. Check balance

**Expected Results:**
- ✓ Balance = Previous + 1000 - 300
- ✓ Updates immediately after each transaction

### Test 8.2: Transaction Edit Impact
**Steps:**
1. Note balance
2. Edit existing transaction amount
3. Verify balance recalculation

**Expected Results:**
- ✓ Balance adjusts correctly
- ✓ Old amount removed, new amount applied

### Test 8.3: Transaction Delete Impact
**Steps:**
1. Note balance
2. Delete a transaction
3. Verify balance

**Expected Results:**
- ✓ Balance adjusts to remove deleted transaction
- ✓ Monthly summaries update

---

## 9. Edge Cases & Error Handling

### Test 9.1: Empty States
**Steps:**
1. New user with no data
2. View each page

**Expected Results:**
- ✓ Dashboard shows helpful empty state messages
- ✓ Transaction list shows "No transactions" message
- ✓ Budget list shows "Create your first budget" prompt

### Test 9.2: Invalid Form Data
**Steps:**
1. Try to submit forms with:
   - Negative amounts
   - Empty required fields
   - Invalid dates
   - Very large numbers

**Expected Results:**
- ✓ Form validation prevents submission
- ✓ Clear error messages displayed
- ✓ No server errors

### Test 9.3: Special Characters
**Steps:**
1. Add transaction with description: `<script>alert('test')</script>`
2. View transaction

**Expected Results:**
- ✓ No script execution (XSS prevention)
- ✓ Characters displayed safely

---

## 10. Performance Tests

### Test 10.1: Many Transactions
**Steps:**
1. Create 100+ transactions
2. Navigate to transaction list
3. Filter and search

**Expected Results:**
- ✓ Pagination works smoothly
- ✓ Page load < 2 seconds
- ✓ Filters respond quickly

### Test 10.2: Dashboard Load Time
**Steps:**
1. With substantial data, load dashboard
2. Measure load time

**Expected Results:**
- ✓ Page loads in < 3 seconds
- ✓ Charts render without delay
- ✓ No JavaScript errors

---

## Test Results Template

Use this template to record test results:

```
Test ID: [e.g., 2.1]
Test Name: [e.g., Add Income Transaction]
Date: [Test date]
Tester: [Your name]
Status: [✓ PASS / ✗ FAIL]
Notes: [Any observations]
Issues Found: [Bug descriptions if any]
```

## Automation Testing (Optional)

Create `tests.py` for automated tests:

```python
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from core.models import Account, Transaction, Category
from decimal import Decimal

User = get_user_model()

class TransactionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.account = Account.objects.get(user=self.user)
        self.category = Category.objects.create(
            name='Test Category',
            type='INCOME',
            is_default=True
        )
    
    def test_balance_update_on_income(self):
        """Test that balance updates when income is added"""
        initial_balance = self.account.balance
        
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.category,
            amount=Decimal('1000.00'),
            type='INCOME',
            date='2024-01-01'
        )
        
        self.account.refresh_from_db()
        self.assertEqual(
            self.account.balance,
            initial_balance + Decimal('1000.00')
        )
```

Run automated tests:
```bash
python manage.py test core
```

---

## Bug Reporting Template

If you find bugs during testing:

```
Bug ID: BUG-001
Severity: [Critical/High/Medium/Low]
Title: [Brief description]
Steps to Reproduce:
1. 
2. 
3. 

Expected Result:
[What should happen]

Actual Result:
[What actually happened]

Environment:
- Browser: [Chrome 120, Firefox 121, etc.]
- OS: [Windows 11, Ubuntu 22.04, etc.]
- Python: [3.11.5]
- Django: [5.0.1]

Screenshots: [Attach if relevant]
```

---

## Testing Sign-Off

After completing all tests:

- [ ] All authentication tests passed
- [ ] All transaction tests passed
- [ ] All budget tests passed
- [ ] All category tests passed
- [ ] Dashboard displays correctly
- [ ] Admin panel functional
- [ ] Responsive design works
- [ ] Data integrity verified
- [ ] Edge cases handled
- [ ] Performance acceptable

**Tested By**: ___________________
**Date**: ___________________
**Signature**: ___________________

---

**Testing Complete! Ready for Deployment ✅**
