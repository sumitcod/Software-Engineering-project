# FinGuard - Architecture & Flow Diagrams

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                  (Browser - Bootstrap 5 + Chart.js)             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTP Requests/Responses
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Templates  │  │    Forms     │  │     URLs     │         │
│  │  (HTML/CSS)  │  │ (Validation) │  │  (Routing)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                           │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    CLASS-BASED VIEWS                      │  │
│  │  Dashboard │ Transaction │ Budget │ Category │ Auth      │  │
│  └─────────────────┬────────────────────────────────────────┘  │
│                    │                                            │
│  ┌─────────────────▼────────────────────────────────────────┐  │
│  │                   SERVICE LAYER                          │  │
│  │  TransactionService  │  BudgetService                    │  │
│  │  - Balance Calc      │  - Status Calc                    │  │
│  │  - Summaries         │  - Alerts                         │  │
│  │  - Filtering         │  - Validation                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                       DOMAIN LAYER                               │
│                                                                  │
│  ┌──────┐  ┌─────────┐  ┌──────────┐  ┌────────┐  ┌────────┐ │
│  │ User │  │ Account │  │Category  │  │Transaction│ │Budget │ │
│  └──────┘  └─────────┘  └──────────┘  └────────┘  └────────┘ │
│                                                                  │
│  Signals: Auto-update balance on transaction save/delete        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                   DATA ACCESS LAYER                              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    DJANGO ORM                             │  │
│  │  QuerySet API │ Aggregations │ Transactions │ Relations  │  │
│  └─────────────────────┬────────────────────────────────────┘  │
└────────────────────────┼────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                      MySQL DATABASE                              │
│  Tables: users, accounts, categories, transactions, budgets     │
└──────────────────────────────────────────────────────────────────┘
```

## 2. Request Flow Diagram

### Example: Creating a Transaction

```
User Action: Click "Add Transaction" → Fill Form → Submit
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│ 1. URL Routing (urls.py)                                   │
│    /transactions/add/ → TransactionCreateView              │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│ 2. View Layer (views.py)                                   │
│    TransactionCreateView.form_valid()                      │
│    - Get user's account                                    │
│    - Set user and account on form instance                 │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│ 3. Form Validation (forms.py)                              │
│    TransactionForm.clean()                                 │
│    - Validate category type matches transaction type       │
│    - Check amount is positive                              │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│ 4. Model Save (models.py)                                  │
│    Transaction.save()                                      │
│    - Validate category type                                │
│    - Save to database                                      │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│ 5. Signal Trigger (signals.py)                             │
│    post_save signal → update_balance_on_transaction_save() │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│ 6. Service Layer (transaction_service.py)                  │
│    TransactionService.recalculate_account_balance()        │
│    - Calculate total income                                │
│    - Calculate total expenses                              │
│    - Update account balance                                │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│ 7. Budget Alert Check (views.py)                           │
│    BudgetService.check_budget_alerts()                     │
│    - Find affected budgets                                 │
│    - Calculate status                                      │
│    - Generate warning messages                             │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│ 8. Response                                                │
│    - Redirect to transaction list                          │
│    - Display success message                               │
│    - Show budget alerts (if any)                           │
└────────────────────────────────────────────────────────────┘
```

## 3. Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER ACTIONS                             │
└────┬───────────┬───────────┬───────────┬───────────┬────────────┘
     │           │           │           │           │
     │Register   │Login      │Add        │Create     │View
     │           │           │Transaction│Budget     │Dashboard
     │           │           │           │           │
     ▼           ▼           ▼           ▼           ▼
┌────────────────────────────────────────────────────────────────┐
│                         DATABASE                                │
│                                                                 │
│  ┌─────────┐    ┌──────────┐    ┌─────────────┐              │
│  │  User   │───▶│ Account  │───▶│Transactions │              │
│  │ Created │    │ Created  │    │   Saved     │              │
│  └─────────┘    └──────────┘    └──────┬──────┘              │
│                                         │                      │
│                                  ┌──────▼──────┐              │
│                                  │Balance Calc │              │
│                                  │(via Signal) │              │
│                                  └─────────────┘              │
│                                                                 │
│  ┌──────────┐    ┌───────────────────┐                        │
│  │ Category │◀───│     Budget        │                        │
│  │ (Default)│    │   with Status     │                        │
│  └──────────┘    └───────────────────┘                        │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                      PROCESSING                                 │
│                                                                 │
│  Services Calculate:                                           │
│  • Account Balance (Income - Expenses)                         │
│  • Budget Status (Spent / Total)                              │
│  • Monthly Summaries                                           │
│  • Expense Breakdowns                                          │
│  • Alert Conditions                                            │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                               │
│                                                                 │
│  Dashboard Displays:                                           │
│  • Current Balance: $4,850.00                                  │
│  • Monthly Income: $5,000.00                                   │
│  • Monthly Expense: $150.00                                    │
│  • Budget Progress: [=====>    ] 50%                          │
│  • Expense Chart: [Pie Chart]                                 │
│  • Recent Transactions List                                    │
│  • Alerts: "⚠️ Food budget at 95%"                            │
└────────────────────────────────────────────────────────────────┘
```

## 4. Database Schema Diagram

```
┌────────────────────┐
│       User         │
│────────────────────│
│ id (PK)            │
│ username           │
│ email              │
│ password           │
│ phone              │
│ is_staff           │
│ date_joined        │
└──────┬─────────────┘
       │ 1:M
       │
       ├──────────────────┐
       │                  │
       ▼                  ▼
┌────────────────────┐   ┌────────────────────┐
│     Account        │   │     Category       │
│────────────────────│   │────────────────────│
│ id (PK)            │   │ id (PK)            │
│ user_id (FK)       │   │ name               │
│ name               │   │ type               │
│ balance            │   │ user_id (FK,NULL)  │
│ created_at         │   │ is_default         │
│ updated_at         │   │ created_at         │
└──────┬─────────────┘   └──────┬─────────────┘
       │ 1:M                     │ 1:M
       │                         │
       └──────────┬──────────────┘
                  │
                  ▼
          ┌────────────────────┐
          │    Transaction     │
          │────────────────────│
          │ id (PK)            │
          │ user_id (FK)       │
          │ account_id (FK)    │
          │ category_id (FK)   │
          │ amount             │
          │ type               │
          │ date               │
          │ description        │
          │ created_at         │
          │ updated_at         │
          └────────────────────┘

┌────────────────────┐
│      Budget        │
│────────────────────│
│ id (PK)            │
│ user_id (FK)  ─────┼──▶ User
│ category_id (FK) ──┼──▶ Category
│ amount             │
│ period_start       │
│ period_end         │
│ created_at         │
│ updated_at         │
└────────────────────┘
```

## 5. Budget Alert Logic Flow

```
Transaction Created/Updated
         │
         ▼
┌──────────────────────────┐
│ Get Active Budgets       │
│ (period includes today)  │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ For Each Budget:         │
│                          │
│ 1. Calculate Spent:      │
│    SUM(transactions)     │
│    WHERE category =      │
│          budget.category │
│    AND date BETWEEN      │
│        period_start      │
│        and period_end    │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Calculate Percentage:    │
│ (Spent / Budget) * 100   │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Determine Status:        │
│                          │
│ IF percentage < 70%:     │
│    status = 'good'       │
│    color = green         │
│                          │
│ ELIF percentage < 90%:   │
│    status = 'warning'    │
│    color = yellow        │
│                          │
│ ELSE:                    │
│    status = 'danger'     │
│    color = red           │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Generate Alerts:         │
│                          │
│ IF percentage >= 90%:    │
│   "⚠️ Budget at XX%"     │
│                          │
│ IF spent > amount:       │
│   "⚠️ Budget exceeded"   │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Display to User:         │
│ - Toast notification     │
│ - Dashboard alert        │
│ - Budget list indicator  │
└──────────────────────────┘
```

## 6. Authentication Flow

```
          ┌───────────────┐
          │  Visit Site   │
          └───────┬───────┘
                  │
          ┌───────▼────────┐
          │ Is Authenticated?│
          └───────┬────────┘
                  │
         ┌────────┴────────┐
         │                 │
    NO   ▼                 ▼  YES
┌─────────────────┐  ┌─────────────────┐
│   Login Page    │  │   Dashboard     │
│                 │  │   (Protected)   │
└────┬───────┬────┘  └─────────────────┘
     │       │
     │       └─────New User
     │
     ▼
┌─────────────────┐
│ Submit Login    │
│ Credentials     │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Authenticate    │
│ User            │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Create Session  │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Redirect to     │
│ Dashboard       │
└─────────────────┘

New User Path:
┌─────────────────┐
│ Register Page   │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Submit Form:    │
│ - Username      │
│ - Email         │
│ - Phone         │
│ - Password      │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Create User     │
└────┬────────────┘
     │
     ▼ (Signal)
┌─────────────────┐
│ Create Account  │
│ (Main Account)  │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Auto Login      │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Dashboard       │
│ Welcome Message │
└─────────────────┘
```

## 7. Service Layer Interaction

```
┌──────────────────────────────────────────────────────────────┐
│                        VIEWS LAYER                           │
│                                                              │
│  TransactionCreateView                                       │
│  BudgetListView                                             │
│  DashboardView                                              │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     │ Calls Services
                     │
┌────────────────────▼─────────────────────────────────────────┐
│                    SERVICE LAYER                             │
│                                                              │
│  ┌────────────────────────────┐  ┌───────────────────────┐ │
│  │  TransactionService        │  │   BudgetService       │ │
│  ├────────────────────────────┤  ├───────────────────────┤ │
│  │ + recalculate_balance()    │  │ + get_budget_status() │ │
│  │ + get_monthly_summary()    │  │ + check_alerts()      │ │
│  │ + get_expenses_by_category │  │ + validate_overlap()  │ │
│  │ + get_filtered_txns()      │  │ + get_active_budgets()│ │
│  │ + create_transaction()     │  │                       │ │
│  │ + update_transaction()     │  │                       │ │
│  │ + delete_transaction()     │  │                       │ │
│  └────────────┬───────────────┘  └──────────┬────────────┘ │
└───────────────┼──────────────────────────────┼───────────────┘
                │                              │
                │ Uses Models                  │
                │                              │
┌───────────────▼──────────────────────────────▼───────────────┐
│                      MODELS LAYER                            │
│                                                              │
│  User, Account, Category, Transaction, Budget               │
│  (Django ORM Queries)                                       │
└──────────────────────────────────────────────────────────────┘
```

## 8. Component Interaction Map

```
┌─────────────────────────────────────────────────────────────────┐
│                       FinGuard Components                        │
└─────────────────────────────────────────────────────────────────┘

urls.py ──────────▶ views.py ──────────▶ forms.py
   │                   │                    │
   │                   │                    │
   │                   ▼                    ▼
   │              services/             models.py
   │                   │                    │
   │                   ▼                    │
   │              transaction_service.py    │
   │              budget_service.py         │
   │                   │                    │
   │                   └─────────┬──────────┘
   │                             │
   │                             ▼
   └──────────────────────▶ templates/ ◀───────┐
                                 │             │
                                 ▼             │
                            base.html          │
                                 │             │
                    ┌────────────┴────────┐    │
                    │                     │    │
                    ▼                     ▼    │
              dashboard.html      transaction_*.html
              budget_*.html       category_*.html
                                  login.html
                                  register.html

signals.py ─────▶ models.py ─────▶ services/
    │                                   │
    │                                   ▼
    └─────────────────────────▶ recalculate_balance()

admin.py ─────▶ models.py
```

---

## Legend

```
┌─────┐
│ Box │  = Component/Module
└─────┘

  │
  ▼      = Data/Control Flow

─────▶   = Direct Call/Reference

(FK)     = Foreign Key
(PK)     = Primary Key
1:M      = One-to-Many Relationship
```

---

This diagram set provides a visual understanding of:
- System architecture layers
- Request processing flow
- Data relationships
- Business logic execution
- Authentication mechanism
- Service layer patterns
- Component interactions

Use these diagrams as reference when:
- Understanding code structure
- Debugging issues
- Adding new features
- Explaining to others
- Documentation
