# FinGuard - Deployment Checklist

## Pre-Deployment

### 1. Code Review
- [ ] All features working in development
- [ ] No debug print statements
- [ ] Code follows PEP 8 standards
- [ ] All imports organized
- [ ] Comments added for complex logic
- [ ] Remove unused code

### 2. Security Configuration

#### settings.py Changes

```python
# CRITICAL: Change these for production

# 1. Secret Key
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
# Generate new: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# 2. Debug Mode
DEBUG = False

# 3. Allowed Hosts
ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
    'your-server-ip',
]

# 4. Database (use environment variables)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# 5. HTTPS/SSL
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 6. HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 3. Environment Variables Setup

Create `.env` file (DO NOT commit to Git):

```bash
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=finguard_db
DB_USER=finguard_prod_user
DB_PASSWORD=strong_password_here
DB_HOST=localhost
DB_PORT=3306

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 4. Database Preparation

```bash
# Backup development data
python manage.py dumpdata > backup.json

# Create production database
mysql -u root -p
```

```sql
CREATE DATABASE finguard_prod CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'finguard_prod_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON finguard_prod.* TO 'finguard_prod_user'@'localhost';
FLUSH PRIVILEGES;
```

```bash
# Run migrations
python manage.py migrate

# Initialize categories
python manage.py init_categories

# Create superuser
python manage.py createsuperuser
```

## Deployment Options

### Option 1: Traditional Server (Ubuntu + Gunicorn + Nginx)

#### Install System Requirements
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
sudo apt install mysql-server nginx
sudo apt install python3.11-dev default-libmysqlclient-dev build-essential
```

#### Install Dependencies
```bash
pip install gunicorn
pip install -r requirements.txt
```

#### Gunicorn Configuration

Create `gunicorn_config.py`:
```python
bind = '127.0.0.1:8000'
workers = 3
worker_class = 'sync'
timeout = 120
accesslog = '/var/log/finguard/gunicorn_access.log'
errorlog = '/var/log/finguard/gunicorn_error.log'
```

#### Systemd Service

Create `/etc/systemd/system/finguard.service`:
```ini
[Unit]
Description=FinGuard Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/finguard
Environment="PATH=/path/to/finguard/venv/bin"
ExecStart=/path/to/finguard/venv/bin/gunicorn -c gunicorn_config.py finguard.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start finguard
sudo systemctl enable finguard
```

#### Nginx Configuration

Create `/etc/nginx/sites-available/finguard`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /path/to/finguard/staticfiles/;
    }

    location /media/ {
        alias /path/to/finguard/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/finguard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### SSL Certificate (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Option 2: Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "finguard.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: finguard_db
      MYSQL_USER: finguard_user
      MYSQL_PASSWORD: strong_password
      MYSQL_ROOT_PASSWORD: root_password
    volumes:
      - mysql_data:/var/lib/mysql

  web:
    build: .
    command: gunicorn finguard.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DB_HOST=db
      - DB_NAME=finguard_db
      - DB_USER=finguard_user
      - DB_PASSWORD=strong_password
    depends_on:
      - db

volumes:
  mysql_data:
  static_volume:
  media_volume:
```

### Option 3: Cloud Platforms

#### Heroku
```bash
# Install Heroku CLI
# Add Procfile
echo "web: gunicorn finguard.wsgi" > Procfile

# Add runtime.txt
echo "python-3.11.0" > runtime.txt

# Deploy
heroku create finguard-app
heroku addons:create cleardb:ignite
heroku config:set DJANGO_SECRET_KEY=your-secret-key
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py init_categories
heroku run python manage.py createsuperuser
```

#### AWS Elastic Beanstalk
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 finguard

# Create environment
eb create finguard-env

# Deploy
eb deploy
```

## Post-Deployment

### 1. Static Files
```bash
python manage.py collectstatic --noinput
```

### 2. Database Optimization
```sql
-- Add indexes (already in models, but verify)
SHOW INDEX FROM transactions;
SHOW INDEX FROM budgets;

-- Optimize tables
OPTIMIZE TABLE transactions;
OPTIMIZE TABLE budgets;
```

### 3. Monitoring Setup

#### Install monitoring tools
```bash
pip install sentry-sdk
```

#### Add to settings.py
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
)
```

### 4. Logging Configuration

Add to settings.py:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/finguard/django_errors.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

### 5. Backup Strategy

#### Automated Database Backup Script
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/finguard"
DB_NAME="finguard_prod"
DB_USER="finguard_prod_user"

mkdir -p $BACKUP_DIR

mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete
```

#### Cron job for daily backup
```bash
crontab -e
# Add: 0 2 * * * /path/to/backup.sh
```

### 6. Performance Optimization

#### settings.py additions
```python
# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Session optimization
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Database connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 600
```

### 7. Testing

```bash
# Run production tests
python manage.py check --deploy

# Test URLs
curl https://yourdomain.com
curl https://yourdomain.com/login/
curl https://yourdomain.com/dashboard/
```

### 8. Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Maintenance

### Daily Tasks
- [ ] Monitor error logs
- [ ] Check server resources (CPU, RAM, Disk)
- [ ] Verify backup completion

### Weekly Tasks
- [ ] Review application logs
- [ ] Check database performance
- [ ] Update dependencies (security patches)

### Monthly Tasks
- [ ] Database optimization
- [ ] Log rotation
- [ ] Security audit
- [ ] Performance review

## Rollback Plan

1. Keep previous version code
2. Maintain database backups
3. Document rollback commands

```bash
# Rollback database
mysql -u user -p database < backup_file.sql

# Rollback code
git checkout previous-version
systemctl restart finguard
```

## Monitoring URLs

- Application: https://yourdomain.com
- Admin Panel: https://yourdomain.com/admin/
- Health Check: https://yourdomain.com/dashboard/ (requires auth)

## Support Contacts

- Server Admin: admin@yourdomain.com
- Database Admin: dba@yourdomain.com
- Developer: dev@yourdomain.com

---

**Deployment Complete! 🚀**

Remember to:
1. Test all features after deployment
2. Monitor logs for first 24 hours
3. Have rollback plan ready
4. Keep backup of working configuration
