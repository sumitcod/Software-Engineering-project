# FinGuard - Quick Setup Guide

## Prerequisites Check

Before starting, ensure you have:
- [ ] Python 3.11+ installed (`python --version`)
- [ ] MySQL 8.0+ installed and running
- [ ] pip package manager
- [ ] Git (optional, for version control)

## Step-by-Step Setup

### 1. Database Setup (5 minutes)

Open MySQL command line or MySQL Workbench:

```sql
-- Create database
CREATE DATABASE finguard_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (optional, can use root)
CREATE USER 'finguard_user'@'localhost' IDENTIFIED BY 'YourSecurePassword123!';

-- Grant privileges
GRANT ALL PRIVILEGES ON finguard_db.* TO 'finguard_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Verify
SHOW DATABASES;
```

### 2. Python Environment Setup (3 minutes)

```bash
# Navigate to project
cd finguard

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Settings (2 minutes)

Edit `finguard/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'finguard_db',
        'USER': 'finguard_user',        # Your MySQL username
        'PASSWORD': 'YourSecurePassword123!',  # Your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

**Important**: Keep your credentials secure! For production, use environment variables.

### 4. Initialize Database (3 minutes)

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Initialize default categories
python manage.py init_categories

# Create admin user
python manage.py createsuperuser
# Enter: username, email (optional), password
```

### 5. Run Development Server (1 minute)

```bash
python manage.py runserver
```

**Open your browser**: http://127.0.0.1:8000

### 6. First Steps in the Application

1. **Register** a new account at http://127.0.0.1:8000/register/
2. **Login** with your credentials
3. **Add a transaction** from the dashboard
4. **Create a budget** to track spending
5. **View reports** on the dashboard

## Verification Checklist

- [ ] Database created successfully
- [ ] All migrations applied without errors
- [ ] Default categories created (13 total)
- [ ] Superuser created
- [ ] Server running without errors
- [ ] Can access login page
- [ ] Can register and login
- [ ] Dashboard loads with charts
- [ ] Can create transactions
- [ ] Can create budgets

## Common Issues & Solutions

### Issue: `mysqlclient` installation fails

**Windows Solution**:
```bash
# Install Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# OR use wheel file
pip install https://download.lfd.uci.edu/pythonlibs/archived/mysqlclient-2.2.0-cp311-cp311-win_amd64.whl
```

**Linux Solution**:
```bash
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install mysqlclient
```

**Mac Solution**:
```bash
brew install mysql
pip install mysqlclient
```

### Issue: Database connection error

Check:
1. MySQL is running: `mysql -u root -p`
2. Database exists: `SHOW DATABASES;`
3. Credentials in `settings.py` are correct
4. Port 3306 is not blocked by firewall

### Issue: Static files not loading

```bash
# Development mode
DEBUG = True  # in settings.py

# Or collect static files
python manage.py collectstatic
```

### Issue: Port 8000 already in use

```bash
# Use different port
python manage.py runserver 8080

# Or kill existing process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

## Admin Panel Access

URL: http://127.0.0.1:8000/admin/

Login with superuser credentials to:
- Manage users
- View all transactions
- Manage categories
- View budgets
- Generate reports

## Testing the Application

### Test Transaction Creation
1. Login as regular user
2. Click "Add Transaction"
3. Select Income type
4. Choose "Salary" category
5. Enter amount: 5000
6. Save
7. Verify balance updated

### Test Budget Alert
1. Create budget: Food - $500
2. Add expense: Food - $480
3. Check for warning message
4. Add expense: Food - $50
5. Check for exceeded alert

### Test Dashboard Charts
1. Add multiple transactions in different categories
2. View dashboard
3. Verify pie chart displays expense breakdown
4. Check monthly summary cards

## Next Steps

1. **Customize Categories**: Add your own expense/income categories
2. **Set Budgets**: Create monthly budgets for key categories
3. **Import Data**: Add historical transactions
4. **Explore Reports**: Use filters to analyze spending
5. **Mobile Access**: Test responsive design on phone

## Production Deployment Checklist

Before deploying to production:

- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Change `SECRET_KEY`
- [ ] Use environment variables for secrets
- [ ] Set up HTTPS/SSL
- [ ] Configure static file serving
- [ ] Set up database backups
- [ ] Enable logging
- [ ] Configure email for password reset
- [ ] Set up monitoring

## Support

For issues or questions:
1. Check README.md for detailed documentation
2. Review Django documentation: https://docs.djangoproject.com
3. Check Bootstrap 5 docs: https://getbootstrap.com
4. Review Chart.js docs: https://www.chartjs.org

## Project Statistics

- **Models**: 5 (User, Account, Category, Transaction, Budget)
- **Views**: 15 (CBVs for all CRUD operations)
- **Templates**: 11 (Base + all pages)
- **Forms**: 6 (with validation)
- **Services**: 2 (Transaction & Budget business logic)
- **Default Categories**: 13 (8 expense + 5 income)

---

**Estimated Total Setup Time**: 15-20 minutes

Good luck with FinGuard! 🚀💰
