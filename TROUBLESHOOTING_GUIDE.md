# Troubleshooting Guide

This comprehensive troubleshooting guide helps you diagnose and resolve common issues with the Brevo Email Automation system. Follow the step-by-step solutions to get your system running smoothly.

## Table of Contents

- [Quick Start Checklist](#quick-start-checklist)
- [Common Issues](#common-issues)
- [API Issues](#api-issues)
- [Database Issues](#database-issues)
- [UI Issues](#ui-issues)
- [Performance Issues](#performance-issues)
- [Security Issues](#security-issues)
- [Advanced Troubleshooting](#advanced-troubleshooting)

## Quick Start Checklist

Before diving into specific issues, run through this checklist:

### ✅ Environment Setup
- [ ] `.env` file exists in project root
- [ ] All required environment variables are set
- [ ] Virtual environment is activated
- [ ] Dependencies are installed (`pip install -r requirements.txt`)

### ✅ Service Status
- [ ] MongoDB connection is working
- [ ] Brevo API key is valid
- [ ] FastAPI server is running on port 5000
- [ ] Streamlit app is accessible on port 8501

### ✅ Configuration
- [ ] API keys have correct permissions
- [ ] Database user has read/write access
- [ ] Email templates exist in Brevo
- [ ] Sender email is verified

## Common Issues

### Issue 1: Application Won't Start

**Symptoms:**
- Streamlit app fails to load
- FastAPI server won't start
- Import errors in console

**Solutions:**

1. **Check Python Version**
   ```bash
   python --version
   # Should be 3.8 or higher
   ```

2. **Verify Dependencies**
   ```bash
   pip list | grep -E "(fastapi|streamlit|pymongo|sib-api)"
   ```

3. **Check Environment Variables**
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('BREVO_API_KEY:', bool(os.getenv('BREVO_API_KEY')))"
   ```

4. **Clear Cache and Restart**
   ```bash
   # Clear Python cache
   find . -type d -name __pycache__ -exec rm -rf {} +
   rm -rf .streamlit/config

   # Restart services
   pkill -f streamlit
   pkill -f uvicorn
   ```

### Issue 2: Login Not Working

**Symptoms:**
- Can't log into the dashboard
- "Invalid username or password" error

**Solutions:**

1. **Check Default Credentials**
   ```python
   # In streamlit_app.py, verify VALID_USERS
   VALID_USERS = {
       "admin": "admin123",
       "user": "user123"
   }
   ```

2. **Reset Password**
   ```python
   # Update VALID_USERS dictionary
   VALID_USERS = {
       "admin": "new_secure_password",
       "your_username": "your_password"
   }
   ```

3. **Clear Browser Cache**
   - Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
   - Clear browser data for localhost

## API Issues

### Issue 3: Brevo API Connection Failed

**Symptoms:**
- "API configuration failed" error
- Campaigns won't schedule
- Templates not loading

**Solutions:**

1. **Verify API Key**
   ```bash
   # Test API key
   curl -H "api-key: YOUR_API_KEY" https://api.brevo.com/v3/account
   ```

2. **Check API Key Permissions**
   - Log in to Brevo dashboard
   - Go to Settings → API Keys
   - Ensure key has permissions for:
     - Contacts
     - Campaigns
     - Templates
     - Senders

3. **Test API Connectivity**
   ```python
   import requests

   API_KEY = "your_api_key"
   response = requests.get(
       "https://api.brevo.com/v3/account",
       headers={"api-key": API_KEY}
   )
   print(f"Status: {response.status_code}")
   print(f"Response: {response.json()}")
   ```

4. **Check Rate Limits**
   - Brevo has rate limits per hour/day
   - Wait and retry if hitting limits
   - Upgrade plan for higher limits

### Issue 4: Template Not Found

**Symptoms:**
- "Template ID does not exist" error
- Campaign scheduling fails

**Solutions:**

1. **Verify Template ID**
   ```bash
   # List all templates
   curl -H "api-key: YOUR_API_KEY" https://api.brevo.com/v3/smtp/templates
   ```

2. **Check Template Status**
   - Templates must be "active" to use
   - Verify template ID in Brevo dashboard

3. **Update Template IDs in Config**
   ```python
   # In config.py
   TEMPLATES = {
       "tuesday": 123,    # Replace with actual IDs
       "friday": 456,
       "post_event": 789
   }
   ```

### Issue 5: Cohort API Integration Issues

**Symptoms:**
- "Error fetching from Cohort API" message
- Cohort emails not loading

**Solutions:**

1. **Verify Cohort API URL**
   ```bash
   # Test cohort API endpoint
   curl -H "Cookie: adminToken=YOUR_ADMIN_TOKEN" YOUR_COHORT_API_URL
   ```

2. **Check Admin Token**
   - Ensure ADMIN_TOKEN is valid and not expired
   - Regenerate token if expired

3. **Test Cohort API Function**
   ```python
   from api import get_cohort_emails

   try:
       emails = get_cohort_emails()
       print(f"Successfully fetched {len(emails)} emails")
   except Exception as e:
       print(f"Error: {e}")
   ```

## Database Issues

### Issue 6: MongoDB Connection Failed

**Symptoms:**
- "MongoDB connection error" messages
- User queries return empty results
- Application startup fails

**Solutions:**

1. **Test Connection String**
   ```python
   from pymongo import MongoClient

   MONGO_URI = "your_mongo_uri"
   client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

   try:
       client.admin.command('ping')
       print("✅ MongoDB connected successfully")
   except Exception as e:
       print(f"❌ Connection failed: {e}")
   finally:
       client.close()
   ```

2. **Check Network Access**
   ```bash
   # Test network connectivity
   ping cluster0.xxxxx.mongodb.net

   # Test port connectivity
   telnet cluster0.xxxxx.mongodb.net 27017
   ```

3. **Verify IP Whitelist**
   - In MongoDB Atlas dashboard
   - Go to Network Access
   - Add your IP address (or 0.0.0.0/0 for testing)

4. **Check Database User Permissions**
   - Ensure user has read/write access
   - Verify database name in connection string

### Issue 7: Empty Query Results

**Symptoms:**
- API endpoints return empty arrays
- No emails found for user segments

**Solutions:**

1. **Check Database Content**
   ```python
   from pymongo import MongoClient

   client = MongoClient("your_mongo_uri")
   db = client["your_database"]

   # Check collection counts
   collections = ['users', 'projects', 'courseprogresses']
   for collection in collections:
       count = db[collection].count_documents({})
       print(f"{collection}: {count} documents")
   ```

2. **Verify Collection Names**
   - Ensure collection names match exactly
   - Check for case sensitivity

3. **Test Specific Queries**
   ```python
   # Test user query
   users = list(db.users.find().limit(5))
   print("Sample users:", users)
   ```

4. **Check Data Format**
   - Verify field names match query expectations
   - Check data types (ObjectId vs string)

## UI Issues

### Issue 8: Streamlit App Not Loading

**Symptoms:**
- Blank page or error messages
- Components not rendering

**Solutions:**

1. **Check Streamlit Version**
   ```bash
   pip show streamlit
   # Should be 1.28.0 or compatible
   ```

2. **Clear Streamlit Cache**
   ```bash
   rm -rf ~/.streamlit/config
   rm -rf .streamlit/config
   ```

3. **Check Port Availability**
   ```bash
   # Kill existing processes
   pkill -f streamlit

   # Check port usage
   lsof -i :8501
   ```

4. **Run with Debug Mode**
   ```bash
   streamlit run streamlit_app.py --logger.level=debug
   ```

### Issue 9: File Upload Issues

**Symptoms:**
- CSV upload fails
- File not processing correctly

**Solutions:**

1. **Check File Format**
   - Ensure CSV has 'email' column
   - Verify UTF-8 encoding
   - Check file size limits

2. **Test File Processing**
   ```python
   import pandas as pd

   # Test CSV reading
   df = pd.read_csv("your_file.csv")
   print("Columns:", df.columns.tolist())
   print("Sample data:", df.head())
   ```

3. **Check File Permissions**
   ```bash
   # Ensure write permissions
   chmod 644 temp_contacts.csv
   ```

## Performance Issues

### Issue 10: Slow API Responses

**Symptoms:**
- API endpoints taking too long
- UI freezing during operations

**Solutions:**

1. **Add Database Indexes**
   ```javascript
   // In MongoDB shell
   db.users.createIndex({ "email": 1 });
   db.users.createIndex({ "createdAt": -1 });
   db.projects.createIndex({ "user_id": 1, "status": 1 });
   ```

2. **Optimize Queries**
   ```python
   # Use limit for large result sets
   results = list(collection.find().limit(1000))

   # Use projection to fetch only needed fields
   results = list(collection.find({}, {"email": 1, "_id": 0}))
   ```

3. **Implement Caching**
   ```python
   import streamlit as st

   @st.cache_data(ttl=3600)  # Cache for 1 hour
   def get_templates():
       # Your template fetching logic
       pass
   ```

### Issue 11: Memory Issues

**Symptoms:**
- Application crashes with memory errors
- Slow performance with large datasets

**Solutions:**

1. **Process Data in Batches**
   ```python
   # Instead of loading all data at once
   batch_size = 1000
   for i in range(0, len(all_emails), batch_size):
       batch = all_emails[i:i + batch_size]
       # Process batch
   ```

2. **Use Generators for Large Datasets**
   ```python
   def get_emails_batch(collection, batch_size=1000):
       cursor = collection.find()
       batch = []
       for doc in cursor:
           batch.append(doc)
           if len(batch) >= batch_size:
               yield batch
               batch = []
       if batch:
           yield batch
   ```

3. **Monitor Memory Usage**
   ```python
   import psutil
   import os

   process = psutil.Process(os.getpid())
   print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
   ```

## Security Issues

### Issue 12: Authentication Bypass

**Symptoms:**
- Unauthorized access to dashboard
- API endpoints accessible without authentication

**Solutions:**

1. **Strengthen Password Requirements**
   ```python
   import re

   def validate_password(password):
       # At least 8 characters, 1 uppercase, 1 lowercase, 1 digit
       pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$'
       return re.match(pattern, password) is not None
   ```

2. **Implement Session Management**
   ```python
   import streamlit as st
   from datetime import datetime, timedelta

   def check_session_timeout():
       if 'last_activity' in st.session_state:
           if datetime.now() - st.session_state.last_activity > timedelta(hours=1):
               st.session_state.authenticated = False
               st.error("Session expired. Please log in again.")
               st.stop()
       st.session_state.last_activity = datetime.now()
   ```

3. **Add IP Whitelisting**
   ```python
   import requests

   ALLOWED_IPS = ['192.168.1.0/24', '10.0.0.0/8']

   def check_ip_allowed(client_ip):
       # Implement IP range checking
       pass
   ```

## Advanced Troubleshooting

### Issue 13: Production Deployment Issues

**Solutions:**

1. **Environment Variables in Production**
   ```bash
   # Use system environment variables instead of .env
   export BREVO_API_KEY="your_prod_key"
   export MONGO_URI="your_prod_mongo_uri"
   ```

2. **SSL Configuration**
   ```python
   # For HTTPS in production
   import ssl

   ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
   ssl_context.load_cert_chain('cert.pem', 'key.pem')
   ```

3. **Process Management**
   ```bash
   # Use PM2 for process management
   npm install -g pm2
   pm2 start "uvicorn user_retention_api:app --host 0.0.0.0 --port 5000" --name api
   pm2 start "streamlit run streamlit_app.py" --name ui
   ```

### Issue 14: Database Migration Issues

**Solutions:**

1. **Backup Data First**
   ```bash
   # MongoDB backup
   mongodump --uri="your_mongo_uri" --out=/path/to/backup
   ```

2. **Test Migration in Staging**
   ```python
   # Test data migration script
   def migrate_data():
       # Your migration logic here
       pass
   ```

3. **Rollback Plan**
   ```bash
   # Restore from backup
   mongorestore --uri="your_mongo_uri" /path/to/backup
   ```

### Issue 15: Integration Testing

**Solutions:**

1. **Create Test Suite**
   ```python
   import unittest
   from unittest.mock import Mock, patch

   class TestAutomationAgent(unittest.TestCase):
       def setUp(self):
           self.agent = AutomationAgent("test_api_key")

       def test_import_contacts(self):
           # Mock the API response
           with patch('requests.post') as mock_post:
               mock_post.return_value.status_code = 200
               result = self.agent.import_contacts("test.csv", "test_list")
               self.assertTrue(result["status"] == "success")
   ```

2. **API Endpoint Testing**
   ```bash
   # Test FastAPI endpoints
   curl -X GET "http://localhost:5000/api/user-retention/emails/users_with_unsubmitted_projects"
   ```

3. **UI Testing**
   ```python
   # Basic UI smoke test
   import streamlit as st

   def test_ui_components():
       # Test login functionality
       # Test data import
       # Test campaign scheduling
       pass
   ```

## Diagnostic Tools

### System Information Script

```python
#!/usr/bin/env python3
"""
System diagnostic script
Run this to gather system information for troubleshooting
"""

import os
import sys
import platform
import subprocess
from dotenv import load_dotenv

def run_command(cmd):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return "", str(e)

def gather_system_info():
    """Gather comprehensive system information"""
    info = {
        "platform": platform.platform(),
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "environment_variables": {}
    }

    # Check key environment variables (without exposing secrets)
    env_vars = ['BREVO_API_KEY', 'MONGO_URI', 'USER_RETENTION_API_URL']
    for var in env_vars:
        info["environment_variables"][var] = bool(os.getenv(var))

    # Check installed packages
    stdout, stderr = run_command("pip list | grep -E '(fastapi|streamlit|pymongo|sib-api)'")
    info["installed_packages"] = stdout

    # Check running processes
    stdout, stderr = run_command("ps aux | grep -E '(streamlit|uvicorn)' | grep -v grep")
    info["running_processes"] = stdout

    # Check port availability
    stdout, stderr = run_command("lsof -i :5000,8501")
    info["port_usage"] = stdout

    return info

def main():
    """Main diagnostic function"""
    print("🔍 Gathering system information...")
    load_dotenv()

    info = gather_system_info()

    print("\n📊 System Information:")
    print("=" * 50)
    for key, value in info.items():
        if isinstance(value, dict):
            print(f"\n{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")

    print("\n✅ Diagnostic complete!")

if __name__ == "__main__":
    main()
```

### Log Analysis Script

```python
#!/usr/bin/env python3
"""
Log analysis script
Analyze application logs for common issues
"""

import re
from collections import Counter

def analyze_logs(log_file):
    """Analyze log file for common patterns"""
    error_patterns = {
        'api_errors': r'API.*error|Error.*API',
        'db_errors': r'MongoDB.*error|Database.*error',
        'auth_errors': r'Authentication.*failed|Login.*error',
        'network_errors': r'Connection.*failed|Timeout',
        'validation_errors': r'Validation.*error|Invalid.*data'
    }

    with open(log_file, 'r') as f:
        content = f.read()

    print("📊 Log Analysis Results:")
    print("=" * 50)

    for error_type, pattern in error_patterns.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            print(f"\n{error_type.replace('_', ' ').title()}: {len(matches)} occurrences")
            # Show most common error messages
            counter = Counter(matches)
            for error, count in counter.most_common(3):
                print(f"  - {error}: {count} times")

    # Check for performance issues
    slow_queries = re.findall(r'duration.*\d+\.\d+s', content, re.IGNORECASE)
    if slow_queries:
        print(f"\n⚠️  Potential Performance Issues: {len(slow_queries)} slow queries detected")

def main():
    """Main analysis function"""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python analyze_logs.py <log_file>")
        sys.exit(1)

    log_file = sys.argv[1]
    analyze_logs(log_file)

if __name__ == "__main__":
    main()
```

## Getting Help

### Support Resources

1. **Documentation**
   - [Brevo API Documentation](https://developers.brevo.com/)
   - [FastAPI Documentation](https://fastapi.tiangolo.com/)
   - [Streamlit Documentation](https://docs.streamlit.io/)
   - [MongoDB Documentation](https://docs.mongodb.com/)

2. **Community Support**
   - GitHub Issues
   - Stack Overflow
   - Reddit communities

3. **Professional Support**
   - Brevo support team
   - MongoDB Atlas support
   - Cloud provider support

### Escalation Process

1. **Level 1**: Check this troubleshooting guide
2. **Level 2**: Review application logs
3. **Level 3**: Test in isolated environment
4. **Level 4**: Contact vendor support
5. **Level 5**: Engage professional services

---

*Troubleshooting Guide v1.2.0 - September 14, 2025*