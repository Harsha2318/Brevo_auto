# Deployment Guide

This guide provides comprehensive instructions for deploying the Brevo Email Automation system in various environments, from local development to production cloud deployments.

## Table of Contents

- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployments](#cloud-deployments)
- [Production Checklist](#production-checklist)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Backup & Recovery](#backup--recovery)

## Local Development

### Quick Start Setup

1. **Clone and Setup**
   ```bash
   git clone https://github.com/Harsha2318/Brevo_auto.git
   cd Brevo_auto
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   nano .env
   ```

3. **Start Services**
   ```bash
   # Terminal 1: Start API server
   uvicorn user_retention_api:app --host 0.0.0.0 --port 5000 --reload

   # Terminal 2: Start Streamlit app
   streamlit run streamlit_app.py
   ```

4. **Access Application**
   - Dashboard: http://localhost:8501
   - API Docs: http://localhost:5000/docs

## Docker Deployment

### Single Container Setup

#### Dockerfile
```dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose ports
EXPOSE 5000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start both services
CMD ["sh", "-c", "uvicorn user_retention_api:app --host 0.0.0.0 --port 5000 & streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]
```

#### Docker Compose (Recommended)

```yaml
version: '3.8'

services:
  brevo-automation:
    build: .
    ports:
      - "5000:5000"  # FastAPI
      - "8501:8501"  # Streamlit
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./temp:/app/temp
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - brevo-network

  mongodb:
    image: mongo:5.0
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
    volumes:
      - mongodb_data:/data/db
      - ./mongo-init:/docker-entrypoint-initdb.d
    restart: unless-stopped
    networks:
      - brevo-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - brevo-network

volumes:
  mongodb_data:
  redis_data:

networks:
  brevo-network:
    driver: bridge
```

### Multi-Container Setup

#### API Container
```dockerfile
# api/Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY user_retention_api.py api.py config.py ./

EXPOSE 5000
CMD ["uvicorn", "user_retention_api:app", "--host", "0.0.0.0", "--port", "5000"]
```

#### UI Container
```dockerfile
# ui/Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY streamlit_app.py brevo_automation.py config.py ./

EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

#### Docker Compose Multi-Service
```yaml
version: '3.8'

services:
  api:
    build: ./api
    ports:
      - "5000:5000"
    env_file:
      - .env
    depends_on:
      - mongodb

  ui:
    build: ./ui
    ports:
      - "8501:8501"
    env_file:
      - .env
    depends_on:
      - api

  mongodb:
    image: mongo:5.0
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_DATABASE: brevo_automation
    volumes:
      - mongodb_data:/data/db

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - api
      - ui

volumes:
  mongodb_data:
```

#### Nginx Configuration
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        server api:5000;
    }

    upstream ui_backend {
        server ui:8501;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # API routes
        location /api/ {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # UI routes
        location / {
            proxy_pass http://ui_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

## Cloud Deployments

### AWS Deployment

#### EC2 Instance Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Clone repository
git clone https://github.com/Harsha2318/Brevo_auto.git
cd Brevo_auto

# Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### AWS Fargate (ECS)
```yaml
# task-definition.json
{
  "family": "brevo-automation",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "brevo-app",
      "image": "your-registry/brevo-automation:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        },
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "DEBUG", "value": "false"}
      ],
      "secrets": [
        {
          "name": "BREVO_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:brevo-api-key"
        },
        {
          "name": "MONGO_URI",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:mongo-uri"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/brevo-automation",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Elastic Beanstalk
```yaml
# .ebextensions/environment.config
option_settings:
  aws:elasticbeanstalk:application:environment:
    ENVIRONMENT: production
    DEBUG: false
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /api: api
  aws:autoscaling:launchconfiguration:
    InstanceType: t3.micro
    IamInstanceProfile: aws-elasticbeanstalk-ec2-role
```

### Google Cloud Platform

#### App Engine
```yaml
# app.yaml
runtime: python39
instance_class: F2

handlers:
- url: /api/.*
  script: auto
  secure: always

- url: /.*
  script: auto
  secure: always

env_variables:
  ENVIRONMENT: production
  DEBUG: false

# Use Cloud Build
# gcloud app deploy
```

#### Cloud Run
```bash
# Build and deploy
gcloud run deploy brevo-automation \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production \
  --set-secrets BREVO_API_KEY=brevo-api-key:latest \
  --set-secrets MONGO_URI=mongo-uri:latest
```

### Microsoft Azure

#### App Service
```json
// arm-template.json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "siteName": {
      "type": "string",
      "metadata": {
        "description": "Name of the web app"
      }
    }
  },
  "resources": [
    {
      "type": "Microsoft.Web/sites",
      "apiVersion": "2020-06-01",
      "name": "[parameters('siteName')]",
      "location": "[resourceGroup().location]",
      "properties": {
        "serverFarmId": "[resourceId('Microsoft.Web/serverfarms', variables('hostingPlanName'))]",
        "siteConfig": {
          "linuxFxVersion": "PYTHON|3.9"
        }
      }
    }
  ]
}
```

#### Azure Container Instances
```bash
# Deploy to ACI
az container create \
  --resource-group myResourceGroup \
  --name brevo-automation \
  --image your-registry/brevo-automation:latest \
  --ports 5000 8501 \
  --environment-variables ENVIRONMENT=production DEBUG=false \
  --secrets brevo-api-key=$BREVO_API_KEY mongo-uri=$MONGO_URI \
  --cpu 1 \
  --memory 1.5
```

### Heroku Deployment

#### Heroku Setup
```bash
# Install Heroku CLI
npm install -g heroku

# Login and create app
heroku login
heroku create brevo-automation

# Set environment variables
heroku config:set BREVO_API_KEY=your_api_key
heroku config:set MONGO_URI=your_mongo_uri
heroku config:set ENVIRONMENT=production

# Deploy
git push heroku main
```

#### Procfile
```
web: uvicorn user_retention_api:app --host=0.0.0.0 --port=$PORT
worker: streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0
```

#### requirements.txt (Heroku)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
streamlit==1.28.0
pymongo==4.6.0
sib-api-v3-sdk==7.6.0
python-dotenv==1.0.0
pandas==2.1.1
requests==2.31.0
python-multipart==0.0.6
gunicorn==21.2.0
```

### Railway Deployment

#### railway.json
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn user_retention_api:app --host=0.0.0.0 --port=$PORT & streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0"
  }
}
```

### Vercel Deployment

#### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "user_retention_api.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "50mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/user_retention_api.py"
    },
    {
      "src": "/(.*)",
      "dest": "/streamlit_app.py"
    }
  ],
  "env": {
    "ENVIRONMENT": "production",
    "DEBUG": "false"
  }
}
```

## Production Checklist

### Pre-Deployment
- [ ] Environment variables configured
- [ ] Database connections tested
- [ ] API keys validated
- [ ] SSL certificates obtained
- [ ] Domain configured
- [ ] DNS records updated

### Security
- [ ] HTTPS enabled
- [ ] API keys secured
- [ ] Database credentials encrypted
- [ ] CORS configured
- [ ] Rate limiting implemented
- [ ] Input validation enabled

### Performance
- [ ] Database indexes created
- [ ] Caching configured
- [ ] CDN setup for static assets
- [ ] Load balancer configured
- [ ] Auto-scaling enabled

### Monitoring
- [ ] Application logs configured
- [ ] Error tracking setup
- [ ] Performance monitoring enabled
- [ ] Health checks implemented
- [ ] Alerts configured

### Backup & Recovery
- [ ] Database backup schedule
- [ ] Application backup procedure
- [ ] Disaster recovery plan
- [ ] Rollback procedure tested

## Monitoring & Maintenance

### Application Monitoring

#### Health Check Endpoints
```python
# In user_retention_api.py
from fastapi import FastAPI, HTTPException
import time

app = FastAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.2.0"
    }

@app.get("/health/detailed")
async def detailed_health():
    """Detailed health check"""
    health_status = {
        "database": check_database_health(),
        "external_apis": check_api_health(),
        "system": check_system_health()
    }

    if not all(health_status.values()):
        raise HTTPException(status_code=503, detail=health_status)

    return health_status
```

#### Logging Configuration
```python
# logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Setup comprehensive logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                'logs/app.log',
                maxBytes=10485760,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )

    # Add request logging
    logging.getLogger('uvicorn.access').setLevel(logging.INFO)
```

#### Metrics Collection
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# Business metrics
EMAILS_SENT = Counter(
    'emails_sent_total',
    'Total emails sent',
    ['campaign_type']
)

ACTIVE_USERS = Gauge(
    'active_users',
    'Number of active users'
)
```

### Database Monitoring

#### Connection Pool Monitoring
```python
# db_monitoring.py
from pymongo import MongoClient
import psutil
import time

class DatabaseMonitor:
    def __init__(self, mongo_uri):
        self.client = MongoClient(mongo_uri)
        self.db = self.client.get_database()

    def get_connection_stats(self):
        """Get database connection statistics"""
        return {
            'active_connections': len(self.client.nodes),
            'available_connections': self.client.maxPoolSize,
            'total_operations': self.db.command('serverStatus')['opcounters']
        }

    def get_performance_metrics(self):
        """Get database performance metrics"""
        return {
            'memory_usage': psutil.virtual_memory().percent,
            'cpu_usage': psutil.cpu_percent(interval=1),
            'db_size': self.db.command('dbStats')['dataSize']
        }
```

### Automated Maintenance

#### Log Rotation
```bash
# logrotate.conf
/app/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 app app
    postrotate
        systemctl reload brevo-automation
    endscript
}
```

#### Database Maintenance
```bash
# MongoDB maintenance script
#!/bin/bash
# db_maintenance.sh

# Create backup
mongodump --db brevo_automation --out /backups/$(date +%Y%m%d_%H%M%S)

# Run maintenance commands
mongo brevo_automation --eval "
  db.users.reIndex();
  db.projects.reIndex();
  db.runCommand({compact: 'users'});
  db.runCommand({compact: 'projects'});
"

# Clean old backups (keep last 7 days)
find /backups -type d -mtime +7 -exec rm -rf {} +
```

#### Automated Updates
```bash
# update.sh
#!/bin/bash

# Pull latest changes
git pull origin main

# Install updates
pip install -r requirements.txt --upgrade

# Run database migrations
python manage.py migrate

# Restart services
sudo systemctl restart brevo-automation-api
sudo systemctl restart brevo-automation-ui

# Health check
curl -f http://localhost/health || echo "Health check failed"
```

## Backup & Recovery

### Database Backup

#### Automated MongoDB Backup
```bash
# backup.sh
#!/bin/bash

BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
MONGO_URI="your_mongo_uri"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
mongodump --uri="$MONGO_URI" --out="$BACKUP_DIR"

# Compress backup
tar -czf "${BACKUP_DIR}.tar.gz" -C /backups "$(basename $BACKUP_DIR)"
rm -rf $BACKUP_DIR

# Upload to cloud storage (optional)
# aws s3 cp "${BACKUP_DIR}.tar.gz" s3://your-backup-bucket/

echo "Backup completed: ${BACKUP_DIR}.tar.gz"
```

#### Point-in-Time Recovery
```bash
# restore.sh
#!/bin/bash

BACKUP_FILE="$1"
MONGO_URI="your_mongo_uri"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Extract backup
tar -xzf "$BACKUP_FILE" -C /tmp

# Restore database
mongorestore --uri="$MONGO_URI" --drop /tmp/$(basename "$BACKUP_FILE" .tar.gz)

echo "Restore completed from: $BACKUP_FILE"
```

### Application Backup

#### Configuration Backup
```bash
# config_backup.sh
#!/bin/bash

BACKUP_DIR="/app/backups/$(date +%Y%m%d_%H%M%S)"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup configuration
cp .env $BACKUP_DIR/
cp config.py $BACKUP_DIR/
cp docker-compose.yml $BACKUP_DIR/

# Backup application code
git archive --format=tar.gz -o "$BACKUP_DIR/app.tar.gz" HEAD

echo "Configuration backup completed: $BACKUP_DIR"
```

### Disaster Recovery

#### Recovery Plan
```yaml
# disaster_recovery.yml
version: '1.0'

objectives:
  - RTO: 4 hours (Recovery Time Objective)
  - RPO: 1 hour (Recovery Point Objective)

recovery_steps:
  1. Assess damage and determine recovery scope
  2. Restore from latest backup
  3. Verify data integrity
  4. Update DNS if necessary
  5. Test application functionality
  6. Notify stakeholders

backup_schedule:
  - Daily: Full database backup
  - Hourly: Configuration backup
  - Real-time: Critical data replication

testing:
  - Monthly: Full recovery test
  - Quarterly: Failover test
  - Annually: Disaster recovery simulation
```

#### Emergency Contacts
```
Technical Lead: tech@company.com
DevOps Team: devops@company.com
Infrastructure: infra@company.com
Business Continuity: bc@company.com
```

---

*Deployment Guide v1.2.0 - September 14, 2025*