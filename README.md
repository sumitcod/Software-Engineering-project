# FinGuard - Personal Finance Management System

A complete, production-ready Django web application for managing personal finances with secure authentication, budget tracking, and financial insights.

## 🚀 Features

### Core Functionality
- **User Authentication**: Custom user model with registration, login, and logout
- **Account Management**: Automatic account creation with real-time balance tracking
- **Transaction Management**: Full CRUD operations for income and expenses
- **Budget Tracking**: Set spending limits with visual progress indicators
- **Category System**: Predefined and custom categories
- **Dashboard**: Real-time financial overview with charts
- **Budget Alerts**: Automatic warnings when approaching or exceeding limits
- **Financial Reports**: Monthly summaries and expense breakdowns

### Technical Features
- Django 5.x with Python 3.11+
- MySQL database with optimized queries
- Layered architecture (Presentation → Business Logic → Domain → Data Access)
- Service layer for business logic separation
- Class-Based Views (CBVs)
- Bootstrap 5 responsive design
- Chart.js for data visualization
- Form validation with django-bootstrap5

## 📋 Requirements

- Python 3.11 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

## 🛠️ Installation & Setup

### 1. Clone/Download the Project

Navigate to the project directory:
```bash
cd finguard
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Requirements include:**
- Django 5.x
- mysqlclient 2.2.0+
- django-bootstrap5 23.3+

### 4. Configure MySQL Database

#### Create Database
```sql
CREATE DATABASE finguard_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'finguard_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON finguard_db.* TO 'finguard_user'@'localhost';
FLUSH PRIVILEGES;
```

#### Update Database Settings

Edit `finguard/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'finguard_db',
        'USER': 'finguard_user',      # Your MySQL username
        'PASSWORD': 'your_password',   # Your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Initialize Default Categories

```bash
python manage.py init_categories
```

This creates default categories:
- **Income**: Salary, Freelance, Investment, Gift, Other
- **Expense**: Food, Rent, Transport, Entertainment, Bills, Shopping, Health, Other

### 7. Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 8. Run Development Server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

## 📁 Project Structure

```
finguard/
├── finguard/                  # Project configuration
│   ├── settings.py           # Django settings
│   ├── urls.py               # Project URLs
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── core/                     # Main application
│   ├── models.py            # Domain models (User, Account, Transaction, Budget, Category)
│   ├── views.py             # Class-Based Views
│   ├── forms.py             # Django forms with validation
│   ├── urls.py              # App URL patterns
│   ├── admin.py             # Admin configuration
│   ├── signals.py           # Signal handlers for balance updates
│   ├── services/            # Business logic layer
│   │   ├── transaction_service.py
│   │   └── budget_service.py
│   ├── templates/           # HTML templates
│   │   ├── base.html
│   │   └── core/
│   │       ├── dashboard.html
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── transaction_*.html
│   │       ├── budget_*.html
│   │       └── category_*.html
│   └── management/
│       └── commands/
│           └── init_categories.py
├── manage.py                # Django management script
└── requirements.txt         # Python dependencies
```

## 🏗️ Architecture

### Layered Design

1. **Presentation Layer**: Django Templates + Bootstrap 5 + Chart.js
   - Responsive UI components
   - Form rendering with django-bootstrap5
   - Interactive charts

2. **Business Logic Layer**: Views → Services
   - Class-Based Views for request handling
   - Service classes for business operations
   - Separation of concerns

3. **Domain Layer**: Models
   - User (Custom AbstractUser)
   - Account (Balance tracking)
   - Category (Income/Expense classification)
   - Transaction (Income/Expense records)
   - Budget (Spending limits)

4. **Data Access Layer**: Django ORM → MySQL
   - Optimized queries with select_related
   - Database indexes
   - Signal-based balance updates

## 🔑 Key Models

### User
- Custom user model extending AbstractUser
- Additional phone field
- Automatic account creation on registration

### Account
- One default "Main Account" per user
- Real-time balance calculated from transactions
- Updated automatically via signals

### Category
- System default categories (Food, Rent, Salary, etc.)
- User-created custom categories
- Type: INCOME or EXPENSE

### Transaction
- Amount, date, category, description
- Type: INCOME or EXPENSE
- Automatically updates account balance
- Validation ensures category type matches transaction type

### Budget
- Monthly spending limits per category
- Period-based (start/end dates)
- Status tracking: good (<70%), warning (70-90%), danger (>90%)
- Overlap validation

## 🎨 User Interface

### Dashboard
- Current balance display
- Monthly income/expense summary
- Recent transactions (last 10)
- Active budgets with progress bars
- Pie chart showing expense breakdown by category
- Budget alerts

### Transactions
- List view with filtering (date range, category, type)
- Pagination (20 per page)
- CRUD operations
- Summary cards (income, expense, net)

### Budgets
- Card layout with visual progress indicators
- Color-coded status (green/yellow/red)
- Spent vs. remaining amounts
- CRUD operations

### Categories
- Separated income/expense views
- Default vs. custom labels
- Easy custom category creation

## 🔐 Security Features

- Django's built-in authentication
- Password validation
- CSRF protection
- LoginRequiredMixin on all protected views
- User-specific data isolation
- SQL injection prevention via ORM

## 📊 Business Logic

### Transaction Service
- `recalculate_account_balance()`: Updates account balance
- `get_monthly_summary()`: Monthly income/expense totals
- `get_expenses_by_category()`: Chart data preparation
- `get_filtered_transactions()`: Advanced filtering

### Budget Service
- `get_budget_status()`: Calculate spent, remaining, percentage
- `check_budget_alerts()`: Generate warning messages
- `validate_budget_overlap()`: Prevent duplicate budgets

## 🎯 Usage Guide

### 1. Register/Login
- Create an account at `/register/`
- Login at `/login/`
- Default "Main Account" created automatically

### 2. Add Transactions
- Click "Add Transaction" from dashboard or transactions page
- Select type (Income/Expense)
- Choose category (filtered by type)
- Enter amount, date, and optional description
- Budget alerts shown if applicable

### 3. Create Budgets
- Navigate to Budgets
- Click "Create Budget"
- Select expense category
- Set amount and period
- View progress on dashboard and budget list

### 4. Custom Categories
- Go to Categories
- Click "Add Custom Category"
- Enter name and type
- Use in transactions and budgets

### 5. View Reports
- Dashboard shows current month expense pie chart
- Transaction list provides filtered summaries
- Budget cards display real-time status

## 🔧 Management Commands

### Initialize Categories
```bash
python manage.py init_categories
```

### Create Migrations
```bash
python manage.py makemigrations
```

### Apply Migrations
```bash
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Collect Static Files (Production)
```bash
python manage.py collectstatic
```

## 🚀 Production Deployment

### Security Checklist

1. **Update SECRET_KEY**:
   ```python
   SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
   ```

2. **Set DEBUG to False**:
   ```python
   DEBUG = False
   ```

3. **Configure ALLOWED_HOSTS**:
   ```python
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   ```

4. **Use Environment Variables**:
   - Database credentials
   - Secret key
   - Email configuration

5. **Set up HTTPS**

6. **Configure Static Files**:
   ```bash
   python manage.py collectstatic
   ```

### Database Optimization

- Enable query caching
- Add database indexes (already included in models)
- Use connection pooling
- Regular backups

## 📱 Responsive Design

- Mobile-first approach
- Bootstrap 5 grid system
- Sidebar collapses on mobile
- Touch-friendly buttons
- Optimized charts for small screens

## 🐛 Troubleshooting

### Database Connection Issues
```python
# Install MySQL client dependencies
pip install mysqlclient

# On Windows, you may need:
# Download MySQL Connector from https://dev.mysql.com/downloads/connector/python/
```

### Migration Errors
```bash
# Reset migrations (development only)
python manage.py migrate core zero
python manage.py migrate
```

### Static Files Not Loading
```bash
python manage.py collectstatic --clear
```

## 📝 API Endpoints

| URL | View | Description |
|-----|------|-------------|
| `/` | RedirectView | Redirect to dashboard |
| `/register/` | RegisterView | User registration |
| `/login/` | LoginView | User login |
| `/logout/` | LogoutView | User logout |
| `/dashboard/` | DashboardView | Main dashboard |
| `/transactions/` | TransactionListView | List transactions |
| `/transactions/add/` | TransactionCreateView | Add transaction |
| `/transactions/<id>/edit/` | TransactionUpdateView | Edit transaction |
| `/transactions/<id>/delete/` | TransactionDeleteView | Delete transaction |
| `/budgets/` | BudgetListView | List budgets |
| `/budgets/add/` | BudgetCreateView | Create budget |
| `/budgets/<id>/edit/` | BudgetUpdateView | Edit budget |
| `/budgets/<id>/delete/` | BudgetDeleteView | Delete budget |
| `/categories/` | CategoryListView | List categories |
| `/categories/add/` | CategoryCreateView | Add category |
| `/admin/` | Admin Site | Django admin panel |

## 🤝 Contributing

This is a complete production-ready application. For customizations:

1. Fork the repository
2. Create feature branch
3. Test thoroughly
4. Submit pull request

## 📄 License

This project is provided as-is for educational and commercial use.

## 👨‍💻 Author

Built with Django 5.x following best practices and layered architecture principles.

---

**FinGuard** - Secure Your Financial Future 🛡️💰
