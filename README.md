# Brevo Email Automation System

A comprehensive email marketing automation platform built with Python, integrating MongoDB for user data, Brevo API for email campaigns, and multiple data sources for targeted email marketing.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Core Functionality
- **Multi-Source Data Integration**: Upload CSV files, fetch from MongoDB queries, or integrate with external cohort APIs
- **Automated Email Campaigns**: Schedule and execute complex email workflows with multiple templates
- **User Segmentation**: Advanced MongoDB queries for user retention and engagement targeting
- **Real-time Dashboard**: Streamlit-based web interface for campaign management
- **Template Management**: Dynamic fetching and validation of Brevo email templates
- **Contact List Management**: Automated creation and management of Brevo contact lists

### Advanced Features
- **Authentication System**: Secure login for dashboard access
- **Error Handling**: Comprehensive error handling and logging
- **API Integration**: RESTful APIs for external integrations
- **Batch Processing**: Efficient bulk email operations
- **Template Validation**: Automatic template activation and validation
- **Scheduling System**: Flexible campaign scheduling with date/time controls

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   FastAPI Server│    │   MongoDB       │
│                 │    │                 │    │                 │
│ - Dashboard     │◄──►│ - REST Endpoints│◄──►│ - User Data     │
│ - Campaign Mgmt │    │ - User Queries  │    │ - Projects      │
│ - Contact Import│    │ - Cohort API    │    │ - Courses       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Brevo API     │
                    │                 │
                    │ - Email Campaigns│
                    │ - Contact Lists │
                    │ - Templates     │
                    │ - Senders       │
                    └─────────────────┘
```

### Components

1. **Streamlit App** (`streamlit_app.py`): Web interface for campaign management
2. **FastAPI Server** (`user_retention_api.py`): REST API for user data queries
3. **MongoDB Queries** (`api.py`): Database operations and user segmentation
4. **Brevo Integration** (`brevo_automation.py`): Email campaign automation
5. **Configuration** (`config.py`): Application settings and constants

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **MongoDB**: Database with user data collections
- **Brevo Account**: API key and verified sender email
- **External APIs**: Cohort API endpoint (optional)

### System Requirements
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 500MB for application and logs
- **Network**: Stable internet connection for API calls

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Harsha2318/Brevo_auto.git
cd Brevo_auto
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

## ⚙️ Configuration

### Environment Variables (.env)

```env
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

# Optional: Gemini API (if using AI features)
GEMINI_API_KEY=your_gemini_api_key_here
```

### Configuration Files

#### config.py
```python
# Brevo API Configuration
API_KEY = os.getenv('BREVO_API_KEY')

# Default sender information
SENDER_INFO = {
    "name": "Your Name",
    "email": "your-email@domain.com"
}

# Template IDs for different campaign types
TEMPLATES = {
    "tuesday": 1,      # Replace with your template IDs
    "friday": 2,
    "post_event": 3
}

# Default paths
CSV_PATH = "contacts.csv"
LIST_NAME = "My Contact List"
```

## 🎯 Usage

### Starting the Application

#### 1. Start FastAPI Server
```bash
# Terminal 1: Start the API server
uvicorn user_retention_api:app --host 0.0.0.0 --port 5000 --reload
```

#### 2. Start Streamlit Dashboard
```bash
# Terminal 2: Start the web interface
streamlit run streamlit_app.py
```

#### 3. Access the Application
- **Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:5000/docs

### Using the Dashboard

#### Login
- **Username**: admin
- **Password**: admin123
- Or create custom users in `VALID_USERS` dictionary

#### Import Contacts
1. Select data source:
   - **Upload CSV**: Upload a CSV file with email column
   - **Fetch from API**: Choose from user retention categories
   - **Fetch from Cohort API**: Get emails from external cohort API
2. Enter list name
3. Click "Import Contacts"

#### Schedule Campaigns
1. Enter campaign name
2. Select email template
3. Choose contact list
4. Set send date and time
5. Select verified sender
6. Click "Schedule Campaign"

#### Execute Workflow
1. Select data source
2. Choose email templates for each campaign type
3. Set event end date
4. Select sender information
5. Click "Execute Workflow"

## 📡 API Endpoints

### User Retention API

All endpoints return a JSON array of email addresses.

#### GET `/api/user-retention/emails/users_with_unsubmitted_projects`
Returns emails of users with unsubmitted projects.

#### GET `/api/user-retention/emails/users_with_incomplete_courses`
Returns emails of users with incomplete course enrollments.

#### GET `/api/user-retention/emails/users_close_to_completing_courses`
Returns emails of users close to completing courses (70-100% progress).

#### GET `/api/user-retention/emails/users_with_unstarted_roadmaps`
Returns emails of users with created but unstarted roadmaps.

#### GET `/api/user-retention/emails/users_with_incomplete_roadmaps`
Returns emails of users with incomplete learning paths.

#### GET `/api/user-retention/emails/users_without_interviews`
Returns emails of users without interview records.

#### GET `/api/user-retention/emails/users_without_resumes`
Returns emails of users without resume files.

#### GET `/api/user-retention/emails/users_for_new_features`
Returns emails of users who joined in the last 30 days.

#### GET `/api/user-retention/emails/users_without_prompt_engineering`
Returns emails of users without prompt engineering submissions.

#### GET `/api/user-retention/emails/users_with_high_scores`
Returns emails of users with Hidevs scores >= 750.

#### GET `/api/user-retention/emails/users_in_talent_pool`
Returns emails of users approved in talent pool (last 7 days).

#### GET `/api/user-retention/emails/users_with_low_talent_scores`
Returns emails of users with talent scores < 60.

#### GET `/api/user-retention/emails/users_with_incomplete_profiles`
Returns emails of users with missing profile information.

### Cohort API Integration

The system integrates with an external cohort API to fetch additional email data:

```python
def get_cohort_emails():
    """Fetch cohort emails from external API."""
    # Uses ADMIN_TOKEN for authentication
    # Returns list of emails from cohort database
```

## 🗄️ Database Schema

### MongoDB Collections

#### Users Collection
```javascript
{
  "_id": ObjectId,
  "email": "user@example.com",
  "full_name": "John Doe",
  "createdAt": ISODate,
  "hidevs_score": 800,
  "created_roadmap": true,
  "roadmap": {
    "completedModules": []
  },
  "resume_file_url": "https://...",
  "linkedin_profile_url": "https://...",
  "github_url": "https://..."
}
```

#### Projects Collection
```javascript
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "status": "Applied", // Applied, Submitted, etc.
  "title": "Project Title",
  "createdAt": ISODate
}
```

#### Course Progress Collection
```javascript
{
  "_id": ObjectId,
  "userId": ObjectId,
  "isEnrolled": true,
  "isCompleted": false,
  "totalProgress": 75
}
```

#### Other Collections
- `interviews`: User interview records
- `learningpaths`: User learning path progress
- `leaderboards`: User ranking data
- `submissions`: User prompt engineering submissions
- `talentpools`: Talent pool entries
- `viewprofiles`: Profile view tracking

## 🔧 Development

### Project Structure
```
Brevo_auto/
├── api.py                    # MongoDB queries and cohort API
├── brevo_automation.py       # Brevo API integration
├── config.py                 # Configuration settings
├── streamlit_app.py          # Main web interface
├── user_retention_api.py     # FastAPI server
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── README.md                 # This file
├── temp_contacts.csv         # Temporary contact storage
└── db/                       # Database related files
```

### Key Classes and Functions

#### AutomationAgent (brevo_automation.py)
- `import_contacts()`: Import CSV contacts to Brevo
- `schedule_campaign()`: Schedule email campaigns
- `execute_workflow()`: Complete campaign workflow
- `get_templates()`: Fetch Brevo templates
- `validate_template_id()`: Validate template existence

#### API Functions (api.py)
- `find_users_with_*()`: Various user segmentation queries
- `get_cohort_emails()`: External cohort API integration
- `write_emails_to_file()`: Export results to files

### Error Handling
The application includes comprehensive error handling:
- API connection failures
- Invalid template IDs
- Database connection issues
- Authentication errors
- File processing errors

### Logging
All operations are logged with detailed error messages and success confirmations.

## 🚀 Deployment

### Local Development
```bash
# Start all services
uvicorn user_retention_api:app --host 0.0.0.0 --port 5000 --reload &
streamlit run streamlit_app.py &
```

### Production Deployment

#### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000 8501

CMD ["uvicorn", "user_retention_api:app", "--host", "0.0.0.0", "--port", "5000"]
```

#### Environment Variables for Production
```env
# Production settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database
MONGO_URI=mongodb+srv://prod-user:prod-pass@prod-cluster.mongodb.net/prod-db

# APIs
BREVO_API_KEY=prod_brevo_key
COHORT_API_URL=https://prod-cohort-api.com/api/cohort/admin/cohort-emails
ADMIN_TOKEN=prod_admin_token
```

### Cloud Deployment Options

#### Streamlit Cloud
1. Connect GitHub repository
2. Set environment variables in Streamlit dashboard
3. Deploy automatically

#### Heroku
```yaml
# Procfile
web: uvicorn user_retention_api:app --host=0.0.0.0 --port=$PORT
worker: streamlit run streamlit_app.py --server.port $PORT
```

#### AWS/GCP/Azure
- Use containerized deployment
- Configure load balancers
- Set up monitoring and logging

## 🔒 Security

### Authentication
- Basic username/password authentication for dashboard
- API token authentication for external integrations
- Environment variable storage for sensitive data

### Best Practices
- Never commit API keys to version control
- Use HTTPS for all API communications
- Regularly rotate API tokens
- Implement rate limiting for API endpoints
- Validate all user inputs

### Data Protection
- Email addresses are hashed when stored locally
- No sensitive user data is cached
- Secure MongoDB connection with authentication
- Encrypted communication with Brevo API

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run specific test file
pytest test_api.py

# Run with coverage
pytest --cov=. --cov-report=html
```

### Test Categories
- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **UI Tests**: Streamlit interface testing
- **Database Tests**: MongoDB query testing

## 📊 Monitoring

### Health Checks
- API endpoint response times
- Database connection status
- Brevo API availability
- Memory and CPU usage

### Logging
- Structured logging with timestamps
- Error tracking and alerting
- Performance metrics
- User activity logs

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

### Code Standards
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Write comprehensive unit tests
- Update documentation for new features

### Commit Guidelines
```bash
# Format: type(scope): description
feat(api): add new user retention endpoint
fix(ui): resolve template validation error
docs(readme): update installation instructions
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

### Documentation
- [Brevo API Documentation](https://developers.brevo.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [MongoDB Documentation](https://docs.mongodb.com/)

### Troubleshooting
- Check API key validity
- Verify MongoDB connection
- Ensure all environment variables are set
- Check network connectivity

### Common Issues
1. **API Key Invalid**: Regenerate Brevo API key
2. **MongoDB Connection Failed**: Check connection string and network access
3. **Template Not Found**: Verify template ID exists in Brevo
4. **Cohort API Error**: Check ADMIN_TOKEN and endpoint URL

---

**Built with ❤️ for efficient email marketing automation**

*Last updated: September 14, 2025*