# Brevo Email Automation API Documentation

## Overview

The Brevo Email Automation system provides RESTful APIs for user data queries and email campaign management. This document details all available endpoints, their parameters, responses, and usage examples.

## Base URL
```
http://localhost:5000
```

## Authentication

### For Cohort API Integration
```http
Authorization: Bearer {ADMIN_TOKEN}
Cookie: adminToken={ADMIN_TOKEN}
```

## Endpoints

### User Retention Email Queries

All user retention endpoints return a JSON array of email addresses matching specific criteria.

#### 1. Users with Unsubmitted Projects
```http
GET /api/user-retention/emails/users_with_unsubmitted_projects
```

**Description**: Returns emails of users who have applied to projects but haven't submitted them.

**Response**:
```json
[
  "user1@example.com",
  "user2@example.com",
  "user3@example.com"
]
```

**Database Query**:
```javascript
// Finds users with project status "Applied"
{ "status": "Applied" }
```

---

#### 2. Users with Incomplete Courses
```http
GET /api/user-retention/emails/users_with_incomplete_courses
```

**Description**: Returns emails of users enrolled in courses but haven't completed them.

**Response**:
```json
[
  "student1@example.com",
  "student2@example.com"
]
```

**Database Query**:
```javascript
// Finds course progress where enrolled=true and completed=false
{ "isEnrolled": true, "isCompleted": false }
```

---

#### 3. Users Close to Completing Courses
```http
GET /api/user-retention/emails/users_close_to_completing_courses
```

**Description**: Returns emails of users with 70-100% course completion progress.

**Response**:
```json
[
  "almostdone1@example.com",
  "almostdone2@example.com"
]
```

**Database Query**:
```javascript
// Finds courses with progress between 70-100%
{ "totalProgress": { "$gte": 70, "$lt": 100 } }
```

---

#### 4. Users with Unstarted Roadmaps
```http
GET /api/user-retention/emails/users_with_unstarted_roadmaps
```

**Description**: Returns emails of users who created roadmaps but haven't started them.

**Response**:
```json
[
  "newbie1@example.com",
  "newbie2@example.com"
]
```

**Database Query**:
```javascript
// Finds users with created_roadmap=true and empty completedModules
{
  "created_roadmap": true,
  "roadmap.completedModules": { "$eq": [] }
}
```

---

#### 5. Users with Incomplete Roadmaps
```http
GET /api/user-retention/emails/users_with_incomplete_roadmaps
```

**Description**: Returns emails of users with incomplete learning paths.

**Response**:
```json
[
  "learner1@example.com",
  "learner2@example.com"
]
```

**Database Query**:
```javascript
// Finds learning paths with unlocked/in_progress levels
{
  "levels.0.status": { "$in": ["unlocked", "in_progress"] },
  "levels.4.status": { "$ne": "completed" }
}
```

---

#### 6. Users Without Interviews
```http
GET /api/user-retention/emails/users_without_interviews
```

**Description**: Returns emails of users who haven't participated in interviews.

**Response**:
```json
[
  "nointerview1@example.com",
  "nointerview2@example.com"
]
```

**Database Query**:
```javascript
// Finds users not in interview collection
{ "_id": { "$nin": interview_user_ids } }
```

---

#### 7. Users Without Resumes
```http
GET /api/user-retention/emails/users_without_resumes
```

**Description**: Returns emails of users without resume files.

**Response**:
```json
[
  "noresume1@example.com",
  "noresume2@example.com"
]
```

**Database Query**:
```javascript
// Finds users with missing or empty resume_file_url
{
  "$or": [
    { "resume_file_url": { "$exists": false } },
    { "resume_file_url": null },
    { "resume_file_url": "" }
  ]
}
```

---

#### 8. Users for New Features
```http
GET /api/user-retention/emails/users_for_new_features
```

**Description**: Returns emails of users who joined in the last 30 days.

**Response**:
```json
[
  "newuser1@example.com",
  "newuser2@example.com"
]
```

**Database Query**:
```javascript
// Finds users created in last 30 days
{ "createdAt": { "$gte": thirty_days_ago } }
```

---

#### 9. Users Without Prompt Engineering
```http
GET /api/user-retention/emails/users_without_prompt_engineering
```

**Description**: Returns emails of users without prompt engineering submissions.

**Response**:
```json
[
  "noprompt1@example.com",
  "noprompt2@example.com"
]
```

**Database Query**:
```javascript
// Finds users not in submissions collection
{ "email": { "$nin": submission_emails } }
```

---

#### 10. Users with High Scores
```http
GET /api/user-retention/emails/users_with_high_scores
```

**Description**: Returns emails of users with Hidevs scores >= 750.

**Response**:
```json
[
  "topperformer1@example.com",
  "topperformer2@example.com"
]
```

**Database Query**:
```javascript
// Finds users with high scores
{ "hidevs_score": { "$gte": 750 } }
```

---

#### 11. Users in Talent Pool
```http
GET /api/user-retention/emails/users_in_talent_pool
```

**Description**: Returns emails of users approved in talent pool (last 7 days).

**Response**:
```json
[
  "talent1@example.com",
  "talent2@example.com"
]
```

**Database Query**:
```javascript
// Finds recent talent pool approvals
{ "approved_date": { "$gte": seven_days_ago } }
```

---

#### 12. Users with Low Talent Scores
```http
GET /api/user-retention/emails/users_with_low_talent_scores
```

**Description**: Returns emails of users with talent scores < 60.

**Response**:
```json
[
  "needshelp1@example.com",
  "needshelp2@example.com"
]
```

**Database Query**:
```javascript
// Finds users with low talent scores
{ "score": { "$lt": 60 } }
```

---

#### 13. Users with Incomplete Profiles
```http
GET /api/user-retention/emails/users_with_incomplete_profiles
```

**Description**: Returns emails of users with missing profile information.

**Response**:
```json
[
  "incomplete1@example.com",
  "incomplete2@example.com"
]
```

**Database Query**:
```javascript
// Finds users missing profile fields
{
  "$or": [
    { "full_name": { "$exists": false } },
    { "full_name": null },
    { "full_name": "" },
    { "linkedin_profile_url": { "$exists": false } },
    { "linkedin_profile_url": null },
    { "linkedin_profile_url": "" },
    { "resume_file_url": { "$exists": false } },
    { "resume_file_url": null },
    { "resume_file_url": "" },
    { "github_url": { "$exists": false } },
    { "github_url": null },
    { "github_url": "" }
  ]
}
```

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-09-14T10:30:00Z"
}
```

### Common Error Codes
- `DATABASE_ERROR`: Database connection or query failed
- `VALIDATION_ERROR`: Invalid request parameters
- `AUTHENTICATION_ERROR`: Authentication failed
- `NOT_FOUND`: Resource not found
- `RATE_LIMITED`: Too many requests

## Rate Limiting

- **Limit**: 100 requests per minute per IP
- **Headers**:
  - `X-RateLimit-Limit`: Maximum requests per minute
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Time when limit resets

## Examples

### Python Client
```python
import requests

BASE_URL = "http://localhost:5000"

def get_user_emails(endpoint):
    response = requests.get(f"{BASE_URL}{endpoint}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return []

# Get users with high scores
high_score_users = get_user_emails("/api/user-retention/emails/users_with_high_scores")
print(f"Found {len(high_score_users)} high-scoring users")
```

### JavaScript Client
```javascript
const BASE_URL = 'http://localhost:5000';

async function fetchUserEmails(endpoint) {
    try {
        const response = await fetch(`${BASE_URL}${endpoint}`);
        if (response.ok) {
            const emails = await response.json();
            console.log(`Found ${emails.length} users`);
            return emails;
        } else {
            console.error(`Error: ${response.status}`);
        }
    } catch (error) {
        console.error('Fetch error:', error);
    }
}

// Usage
fetchUserEmails('/api/user-retention/emails/users_with_unsubmitted_projects');
```

### cURL Examples
```bash
# Get users with incomplete courses
curl -X GET "http://localhost:5000/api/user-retention/emails/users_with_incomplete_courses" \
     -H "accept: application/json"

# Get users for new features
curl -X GET "http://localhost:5000/api/user-retention/emails/users_for_new_features" \
     -H "accept: application/json"
```

## Integration Examples

### Brevo Campaign Integration
```python
import requests
from datetime import datetime

def create_targeted_campaign(user_segment, template_id, list_name):
    # 1. Get user emails from API
    response = requests.get(f"http://localhost:5000/api/user-retention/emails/{user_segment}")
    emails = response.json()
    
    # 2. Create CSV for Brevo import
    csv_content = "email\n" + "\n".join(emails)
    
    # 3. Import to Brevo (simplified)
    # ... Brevo API calls ...
    
    return f"Campaign created for {len(emails)} users"
```

### Automated Weekly Reports
```python
def generate_weekly_report():
    segments = [
        'users_with_unsubmitted_projects',
        'users_with_incomplete_courses',
        'users_for_new_features'
    ]
    
    report = {}
    for segment in segments:
        response = requests.get(f"http://localhost:5000/api/user-retention/emails/{segment}")
        emails = response.json()
        report[segment] = len(emails)
    
    return report
```

## Monitoring

### Health Check
```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-09-14T10:30:00Z"
}
```

### Metrics
```http
GET /metrics
```

**Response**:
```json
{
  "total_requests": 1250,
  "active_connections": 5,
  "response_time_avg": 0.234,
  "error_rate": 0.02
}
```

## Versioning

API versioning follows semantic versioning:
- **v1.0.0**: Initial release with basic user retention queries
- **v1.1.0**: Added cohort API integration
- **v1.2.0**: Enhanced error handling and rate limiting

## Changelog

### v1.2.0 (Latest)
- Added comprehensive error handling
- Implemented rate limiting
- Enhanced logging and monitoring
- Added health check endpoints

### v1.1.0
- Integrated cohort API functionality
- Added authentication for external APIs
- Improved database query performance

### v1.0.0
- Initial release with 13 user retention endpoints
- Basic MongoDB integration
- FastAPI framework implementation

---

*API Documentation v1.2.0 - September 14, 2025*