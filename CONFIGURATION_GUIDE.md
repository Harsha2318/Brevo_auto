# Configuration Guide

This guide provides detailed instructions for configuring the Brevo Email Automation system, including environment setup, API keys, database connections, and advanced configuration options.

## Table of Contents

- [Environment Setup](#environment-setup)
- [API Configuration](#api-configuration)
- [Database Configuration](#database-configuration)
- [Authentication Setup](#authentication-setup)
- [Advanced Configuration](#advanced-configuration)
- [Troubleshooting Configuration](#troubleshooting-configuration)

## Environment Setup

### 1. Create Environment File

Create a `.env` file in the project root directory:

```bash
touch .env
```

### 2. Basic Environment Template

```env
# ===========================================
# BREVO EMAIL AUTOMATION CONFIGURATION
# ===========================================

# Brevo API Configuration
BREVO_API_KEY=your_brevo_api_key_here
API_KEY=your_brevo_api_key_here

# MongoDB Configuration
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database

# API Endpoints
USER_RETENTION_API_URL=http://localhost:5000/api/user-retention/emails
COHORT_API_URL=http://localhost:5000/api/cohort/admin/cohort-emails

# Authentication
ADMIN_TOKEN=your_admin_token_here

# Optional AI Features
GEMINI_API_KEY=your_gemini_api_key_here

# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

## API Configuration

### Brevo API Setup

#### 1. Get Brevo API Key
1. Log in to your [Brevo account](https://app.brevo.com/)
2. Go to **Settings** → **API Keys**
3. Click **Create a new API key**
4. Copy the generated API key

#### 2. Verify Sender Email
1. In Brevo dashboard, go to **Senders & IP**
2. Add and verify your sender email address
3. Note the sender name and email for configuration

#### 3. Create Email Templates
1. Go to **Email Templates** in Brevo
2. Create templates for different campaign types:
   - Tuesday Invitation
   - Friday Reminder
   - Post-Event Survey
3. Note the template IDs for configuration

### Environment Variables for Brevo

```env
# Required
BREVO_API_KEY=xkeysib-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
API_KEY=xkeysib-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Default sender (configured in config.py)
DEFAULT_SENDER_NAME=Your Company Name
DEFAULT_SENDER_EMAIL=noreply@yourcompany.com
```

### Testing Brevo Connection

```python
import requests

API_KEY = "your_brevo_api_key"
headers = {"api-key": API_KEY}

# Test API connection
response = requests.get("https://api.brevo.com/v3/account", headers=headers)
if response.status_code == 200:
    print("✅ Brevo API connection successful")
else:
    print(f"❌ Brevo API connection failed: {response.status_code}")
```

## Database Configuration

### MongoDB Atlas Setup

#### 1. Create MongoDB Atlas Cluster
1. Sign up for [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a new cluster (free tier available)
3. Set up database user with read/write permissions
4. Whitelist your IP address or use 0.0.0.0/0 for testing

#### 2. Get Connection String
1. In Atlas dashboard, click **Connect**
2. Choose **Connect your application**
3. Copy the connection string
4. Replace `<password>` with your database user password

#### 3. Environment Configuration

```env
# MongoDB Connection
MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/database_name?retryWrites=true&w=majority
```

### Database Collections Setup

The system expects the following MongoDB collections:

```javascript
// Required collections
db.users
db.projects
db.courseprogresses
db.interviews
db.learningpaths
db.leaderboards
db.submissions
db.talentpools
db.viewprofiles
db.projectsubmissions
```

### Database Connection Testing

```python
from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

try:
    # Test connection
    db = client.test
    db.command('ping')
    print("✅ MongoDB connection successful")

    # List available databases
    print("Available databases:")
    for db_name in client.list_database_names():
        print(f"  - {db_name}")

except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
finally:
    client.close()
```

## Authentication Setup

### Dashboard Authentication

#### Basic Authentication (Default)

```python
# In streamlit_app.py, modify VALID_USERS
VALID_USERS = {
    "admin": "your_secure_password",
    "user1": "password1",
    "user2": "password2"
}
```

#### Advanced Authentication Options

For production, consider implementing:
- OAuth2 with Google/Microsoft
- LDAP integration
- JWT tokens
- Database-backed user management

### API Authentication

#### Cohort API Token

```env
# Admin token for cohort API access
ADMIN_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Token Generation

```python
import jwt
import datetime

def generate_admin_token(secret_key, user_id):
    payload = {
        'adminId': user_id,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token
```

## Advanced Configuration

### Application Settings

```env
# Environment
ENVIRONMENT=production  # development, staging, production
DEBUG=false
LOG_LEVEL=WARNING

# Server Configuration
HOST=0.0.0.0
PORT=5000
WORKERS=4

# Security
SECRET_KEY=your-secret-key-here
SESSION_TIMEOUT=3600

# Performance
MAX_WORKERS=10
REQUEST_TIMEOUT=30
RATE_LIMIT=100

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=csv,txt
```

### Email Campaign Configuration

#### Template Configuration

```python
# In config.py
TEMPLATES = {
    "tuesday": 123,        # Template ID for Tuesday campaigns
    "friday": 456,         # Template ID for Friday campaigns
    "post_event": 789,     # Template ID for post-event surveys
    "welcome": 101,        # Template ID for welcome emails
    "newsletter": 202      # Template ID for newsletters
}
```

#### Campaign Scheduling

```python
# Default scheduling configuration
CAMPAIGN_SCHEDULES = {
    "tuesday": {
        "day": 1,  # Monday=0, Tuesday=1, etc.
        "hour": 9,
        "timezone": "UTC"
    },
    "friday": {
        "day": 4,
        "hour": 9,
        "timezone": "UTC"
    },
    "post_event": {
        "delay_days": 2,
        "hour": 10,
        "timezone": "UTC"
    }
}
```

### Database Optimization

#### Connection Pool Settings

```python
# MongoDB connection configuration
mongo_config = {
    'maxPoolSize': 10,
    'serverSelectionTimeoutMS': 5000,
    'socketTimeoutMS': 45000,
    'connectTimeoutMS': 30000,
    'retryWrites': True,
    'retryReads': True
}
```

#### Indexing Strategy

```javascript
// Recommended indexes for performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "createdAt": -1 });
db.users.createIndex({ "hidevs_score": -1 });
db.projects.createIndex({ "user_id": 1, "status": 1 });
db.courseprogresses.createIndex({ "userId": 1, "isCompleted": 1 });
db.talentpools.createIndex({ "approved_date": -1 });
```

## External API Integration

### Cohort API Configuration

```env
# Cohort API settings
COHORT_API_URL=https://your-cohort-api.com/api/cohort/admin/cohort-emails
COHORT_API_TIMEOUT=30
COHORT_API_RETRIES=3
```

### Third-party Service Integration

```env
# Optional: Analytics
GOOGLE_ANALYTICS_ID=GA_MEASUREMENT_ID

# Optional: Error tracking
SENTRY_DSN=your_sentry_dsn

# Optional: Email service monitoring
MAILGUN_API_KEY=your_mailgun_key
```

## Security Configuration

### SSL/TLS Setup

```python
# For HTTPS in production
ssl_config = {
    'certfile': '/path/to/cert.pem',
    'keyfile': '/path/to/key.pem',
    'ssl_version': ssl.PROTOCOL_TLSv1_2
}
```

### CORS Configuration

```python
# CORS settings for API access
cors_config = {
    'origins': ['https://yourdomain.com'],
    'methods': ['GET', 'POST', 'PUT', 'DELETE'],
    'allow_headers': ['*'],
    'expose_headers': ['X-Total-Count'],
    'supports_credentials': True
}
```

## Monitoring and Logging

### Logging Configuration

```python
import logging

logging_config = {
    'version': 1,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'formatter': 'detailed',
            'level': 'INFO'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
            'level': 'DEBUG'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}
```

### Health Check Endpoints

```python
# Health check configuration
health_checks = {
    'database': True,
    'external_apis': True,
    'file_system': True,
    'memory_usage': True
}
```

## Troubleshooting Configuration

### Common Configuration Issues

#### 1. Brevo API Connection Failed
```bash
# Test API key
curl -H "api-key: YOUR_API_KEY" https://api.brevo.com/v3/account

# Check API key permissions
# Ensure key has necessary permissions for contacts, campaigns, templates
```

#### 2. MongoDB Connection Issues
```bash
# Test connection
mongosh "mongodb+srv://username:password@cluster.mongodb.net/database"

# Check network access
telnet cluster0.xxxxx.mongodb.net 27017

# Verify IP whitelist in Atlas
```

#### 3. Environment Variables Not Loading
```python
# Debug environment loading
import os
from dotenv import load_dotenv

load_dotenv()
print("BREVO_API_KEY:", os.getenv("BREVO_API_KEY"))
print("MONGO_URI:", os.getenv("MONGO_URI"))
```

#### 4. Template ID Validation Errors
```python
# Check template existence
import requests

API_KEY = "your_api_key"
template_id = 123

response = requests.get(
    f"https://api.brevo.com/v3/smtp/templates/{template_id}",
    headers={"api-key": API_KEY}
)

if response.status_code == 200:
    print("Template exists")
else:
    print(f"Template not found: {response.status_code}")
```

### Configuration Validation Script

```python
#!/usr/bin/env python3
"""
Configuration validation script
Run this to verify all settings are correct
"""

import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv

def validate_configuration():
    """Validate all configuration settings"""
    load_dotenv()
    
    issues = []
    
    # Check required environment variables
    required_vars = [
        'BREVO_API_KEY',
        'MONGO_URI',
        'USER_RETENTION_API_URL'
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            issues.append(f"Missing environment variable: {var}")
    
    # Test Brevo API
    api_key = os.getenv('BREVO_API_KEY')
    if api_key:
        try:
            response = requests.get(
                "https://api.brevo.com/v3/account",
                headers={"api-key": api_key}
            )
            if response.status_code != 200:
                issues.append(f"Brevo API test failed: {response.status_code}")
        except Exception as e:
            issues.append(f"Brevo API connection error: {e}")
    
    # Test MongoDB connection
    mongo_uri = os.getenv('MONGO_URI')
    if mongo_uri:
        try:
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            client.close()
        except Exception as e:
            issues.append(f"MongoDB connection error: {e}")
    
    # Report results
    if issues:
        print("❌ Configuration Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ All configuration checks passed!")
        return True

if __name__ == "__main__":
    validate_configuration()
```

### Production Checklist

- [ ] Environment variables set correctly
- [ ] API keys have proper permissions
- [ ] Database connections working
- [ ] SSL certificates configured
- [ ] CORS settings appropriate
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Backup procedures in place
- [ ] Security headers configured

---

*Configuration Guide v1.2.0 - September 14, 2025*