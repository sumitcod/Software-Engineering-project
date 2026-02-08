# FinGuard - Quick Reference Guide

## Quick Start Commands

### Initial Setup
```bash
# Create virtual environment
python -m venv venv

# Activate environment
venv\Scripts\activate              # Windows
source venv/bin/activate           # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate
python manage.py init_categories
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## Common Django Commands

### Database
```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations
python manage.py showmigrations

# Reverse migrations
python manage.py migrate core zero

# SQL for migrations
python manage.py sqlmigrate core 0001
```

### User Management
```bash
# Create superuser
python manage.py createsuperuser

# Change user password
python manage.py changepassword username
```

### Data Management
```bash
# Backup data
python manage.py dumpdata > backup.json
python manage.py dumpdata core > core_backup.json

# Restore data
python manage.py loaddata backup.json

# Clear all data (DANGER!)
python manage.py flush
```

### Shell Commands
```bash
# Open Django shell
python manage.py shell

# Common shell operations
>>> from core.models import User, Transaction, Budget
>>> User.objects.all()
>>> Transaction.objects.filter(user__username='testuser')
>>> from decimal import Decimal
>>> Transaction.objects.create(...)
```

## MySQL Commands

### Database Management
```sql
-- Connect to MySQL
mysql -u root -p

-- Show databases
SHOW DATABASES;

-- Use database
USE finguard_db;

-- Show tables
SHOW TABLES;

-- Describe table
DESCRIBE transactions;

-- Count records
SELECT COUNT(*) FROM transactions;

-- View recent transactions
SELECT * FROM transactions ORDER BY date DESC LIMIT 10;

-- Backup database
mysqldump -u root -p finguard_db > backup.sql

-- Restore database
mysql -u root -p finguard_db < backup.sql

-- Delete database (DANGER!)
DROP DATABASE finguard_db;
```

### Query Examples
```sql
-- Total income
SELECT SUM(amount) FROM transactions WHERE type='INCOME';

-- Total expenses
SELECT SUM(amount) FROM transactions WHERE type='EXPENSE';

-- Transactions by category
SELECT c.name, COUNT(*), SUM(t.amount)
FROM transactions t
JOIN categories c ON t.category_id = c.id
GROUP BY c.name;

-- Users with most transactions
SELECT u.username, COUNT(t.id) as transaction_count
FROM users u
LEFT JOIN transactions t ON u.id = t.user_id
GROUP BY u.username
ORDER BY transaction_count DESC;

-- Budget status
SELECT b.*, c.name as category_name,
       (SELECT SUM(amount) FROM transactions 
        WHERE category_id = b.category_id 
        AND date BETWEEN b.period_start AND b.period_end
        AND type='EXPENSE') as spent
FROM budgets b
JOIN categories c ON b.category_id = c.id;
```

## Git Commands

### Basic Operations
```bash
# Initialize repository
git init

# Add files
git add .
git add filename

# Commit changes
git commit -m "Commit message"

# View status
git status

# View history
git log
git log --oneline

# Push to remote
git push origin main

# Pull from remote
git pull origin main
```

### Branching
```bash
# Create branch
git branch feature-name

# Switch branch
git checkout feature-name

# Create and switch
git checkout -b feature-name

# Merge branch
git checkout main
git merge feature-name

# Delete branch
git branch -d feature-name
```

## Virtual Environment

### Windows
```bash
# Create
python -m venv venv

# Activate
venv\Scripts\activate

# Deactivate
deactivate

# Remove
rmdir /s venv
```

### Linux/Mac
```bash
# Create
python3 -m venv venv

# Activate
source venv/bin/activate

# Deactivate
deactivate

# Remove
rm -rf venv
```

## Package Management

```bash
# Install package
pip install package-name

# Install specific version
pip install package-name==1.0.0

# Install from requirements
pip install -r requirements.txt

# Update package
pip install --upgrade package-name

# Uninstall package
pip uninstall package-name

# List installed packages
pip list

# Show package info
pip show package-name

# Generate requirements
pip freeze > requirements.txt

# Check outdated packages
pip list --outdated
```

## Server Management

### Development Server
```bash
# Default (port 8000)
python manage.py runserver

# Custom port
python manage.py runserver 8080

# All interfaces
python manage.py runserver 0.0.0.0:8000

# Stop server
Ctrl+C
```

### Production Server (Gunicorn)
```bash
# Install
pip install gunicorn

# Run
gunicorn finguard.wsgi:application

# With config
gunicorn -c gunicorn_config.py finguard.wsgi:application

# With workers
gunicorn --workers 3 --bind 0.0.0.0:8000 finguard.wsgi:application
```

## Static Files

```bash
# Collect static files
python manage.py collectstatic

# Clear and recollect
python manage.py collectstatic --clear --noinput

# Link static files (dev)
python manage.py collectstatic --link
```

## Debugging

### Django Shell
```bash
# Open shell
python manage.py shell

# Test query
>>> from core.models import Transaction
>>> Transaction.objects.all()

# Test service
>>> from core.services.transaction_service import TransactionService
>>> TransactionService.get_monthly_summary(user)

# Test balance calculation
>>> from core.models import Account
>>> account = Account.objects.first()
>>> from core.services.transaction_service import TransactionService
>>> TransactionService.recalculate_account_balance(account)
```

### Django Debug Toolbar (Optional)
```bash
# Install
pip install django-debug-toolbar

# Add to INSTALLED_APPS in settings.py
'debug_toolbar',

# Add to MIDDLEWARE
'debug_toolbar.middleware.DebugToolbarMiddleware',

# Add to urls.py
import debug_toolbar
urlpatterns = [
    path('__debug__/', include(debug_toolbar.urls)),
] + urlpatterns
```

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test core

# Run specific test case
python manage.py test core.tests.TransactionTestCase

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Logs

### View Logs
```bash
# Django logs
tail -f /var/log/finguard/django.log

# Gunicorn logs
tail -f /var/log/finguard/gunicorn_error.log

# Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# System logs
journalctl -u finguard -f
```

## Maintenance

### Database Optimization
```sql
-- Analyze tables
ANALYZE TABLE transactions;
ANALYZE TABLE budgets;

-- Optimize tables
OPTIMIZE TABLE transactions;
OPTIMIZE TABLE budgets;

-- Check table status
SHOW TABLE STATUS;

-- Repair table
REPAIR TABLE transactions;
```

### Clear Cache
```bash
# Django cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()

# Browser cache
Clear in browser settings or use Ctrl+Shift+R
```

## Environment Variables

### Set Environment Variables

#### Windows
```bash
# Temporary
set DJANGO_SECRET_KEY=your-secret-key
set DEBUG=False

# Permanent
setx DJANGO_SECRET_KEY "your-secret-key"
```

#### Linux/Mac
```bash
# Temporary
export DJANGO_SECRET_KEY=your-secret-key
export DEBUG=False

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export DJANGO_SECRET_KEY=your-secret-key' >> ~/.bashrc
source ~/.bashrc
```

#### Using .env file
```bash
# Install python-decouple
pip install python-decouple

# Create .env file
echo "DJANGO_SECRET_KEY=your-secret-key" > .env
echo "DEBUG=False" >> .env

# Use in settings.py
from decouple import config
SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
```

## Troubleshooting

### Common Issues

#### Port already in use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

#### Permission denied
```bash
# Linux/Mac
sudo chown -R $USER:$USER .
chmod +x manage.py
```

#### Module not found
```bash
pip install -r requirements.txt
pip install package-name
```

#### Database connection error
```bash
# Check MySQL is running
# Windows
net start MySQL80

# Linux
sudo systemctl start mysql
sudo systemctl status mysql

# Mac
brew services start mysql
```

## Useful URLs

| Purpose | URL |
|---------|-----|
| Homepage | http://127.0.0.1:8000/ |
| Login | http://127.0.0.1:8000/login/ |
| Register | http://127.0.0.1:8000/register/ |
| Dashboard | http://127.0.0.1:8000/dashboard/ |
| Transactions | http://127.0.0.1:8000/transactions/ |
| Budgets | http://127.0.0.1:8000/budgets/ |
| Categories | http://127.0.0.1:8000/categories/ |
| Admin | http://127.0.0.1:8000/admin/ |

## Keyboard Shortcuts

### VS Code
- `Ctrl+Shift+P` - Command Palette
- `Ctrl+`` - Toggle Terminal
- `Ctrl+B` - Toggle Sidebar
- `F5` - Start Debugging
- `Ctrl+/` - Comment/Uncomment

### Django Shell
- `Ctrl+D` or `exit()` - Exit shell
- `Up Arrow` - Previous command
- `Tab` - Auto-complete

### Browser
- `F12` - Developer Tools
- `Ctrl+Shift+R` - Hard Reload
- `Ctrl+Shift+I` - Inspect Element

## Quick Fixes

### Reset Database
```bash
# Backup first!
python manage.py dumpdata > backup.json

# Drop and recreate
mysql -u root -p
DROP DATABASE finguard_db;
CREATE DATABASE finguard_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit

# Migrate
python manage.py migrate
python manage.py init_categories
python manage.py loaddata backup.json
```

### Reset Migrations
```bash
# Delete migration files (except __init__.py)
# In core/migrations/, keep only __init__.py

# Recreate
python manage.py makemigrations
python manage.py migrate
```

### Fix Balance Issues
```bash
python manage.py shell

>>> from core.models import Account
>>> from core.services.transaction_service import TransactionService
>>> for account in Account.objects.all():
...     TransactionService.recalculate_account_balance(account)
...     print(f"Updated {account}")
```

---

## Need Help?

- **Documentation**: Check README.md and SETUP_GUIDE.md
- **Django Docs**: https://docs.djangoproject.com
- **Stack Overflow**: https://stackoverflow.com/questions/tagged/django
- **GitHub Issues**: Create issue in repository

---

**Keep this file handy for quick reference! 📚**
