import os
import sys
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    print("Error: MONGO_URI not set in environment variables.")
    sys.exit(1)

client = MongoClient(MONGO_URI)
# Try to get database name from URI, else fallback to 'hidevstest'
from urllib.parse import urlparse
parsed = urlparse(MONGO_URI)
db_name = parsed.path.lstrip('/') if parsed.path and parsed.path != '/' else 'hidevstest'
if not db_name:
    print("Error: No database name found in MONGO_URI. Please specify it in the URI.")
    sys.exit(1)
db = client[db_name]

# Collections
User = db["users"]
Project = db["projects"]
CourseProgress = db["courseprogresses"]
Interview = db["interviews"]
LearningPath = db["learningpaths"]
Leaderboard = db["leaderboards"]
Submission = db["submissions"]
TalentPool = db["talentpools"]
ViewProfile = db["viewprofiles"]
ProjectSubmission = db["projectsubmissions"]

# Output directory
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def write_emails_to_file(emails, filename):
    if not emails:
        print(f"No emails found for {filename}")
        return
    file_path = os.path.join(OUTPUT_DIR, f"{filename}.txt")
    with open(file_path, "w") as f:
        f.write("\n".join(emails))
    print(f"Wrote {len(emails)} emails to {file_path}")


# -------------------------
# Queries
# -------------------------

def find_users_with_unsubmitted_projects(write_to_file=False):
    # Use aggregation to mimic Mongoose's populate for user_id and email
    pipeline = [
        {"$match": {"status": "Applied"}},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user"
        }},
        {"$unwind": "$user"},
        {"$project": {"email": "$user.email"}}
    ]
    print(list(Project.aggregate(pipeline)))
    results = list(Project.aggregate(pipeline))
    emails = [r.get("email") for r in results if r.get("email")]
    emails = list(set(emails))
    if write_to_file:
        write_emails_to_file(emails, "users_with_unsubmitted_projects")
    return emails


def find_users_with_incomplete_enrollments(write_to_file=False):
    courses = list(CourseProgress.find({"isEnrolled": True, "isCompleted": False}, {"userId": 1}))
    emails = []
    for course in courses:
        user = User.find_one({"_id": course["userId"]}, {"email": 1})
        if user and user.get("email"):
            emails.append(user["email"])
    emails = list(set(emails))
    if write_to_file:
        write_emails_to_file(emails, "users_with_incomplete_courses")
    return emails


def find_users_close_to_completing_courses(write_to_file=False):
    courses = list(CourseProgress.find({
        "isCompleted": False,
        "totalProgress": {"$gte": 70, "$lt": 100}
    }, {"userId": 1}))

    emails = []
    for course in courses:
        user = User.find_one({"_id": course["userId"]}, {"email": 1})
        if user and user.get("email"):
            emails.append(user["email"])
    emails = list(set(emails))
    if write_to_file:
        write_emails_to_file(emails, "users_close_to_completing_courses")
    return emails


def find_users_with_unstarted_roadmaps(write_to_file=False):
    users = list(User.find({
        "created_roadmap": True,
        "roadmap": {"$ne": None},
        "roadmap.completedModules": {"$eq": []}
    }, {"email": 1}))

    emails = [u["email"] for u in users if u.get("email")]
    if write_to_file:
        write_emails_to_file(emails, "users_with_unstarted_roadmaps")
    return emails


def find_users_with_incomplete_roadmaps(write_to_file=False):
    paths = list(LearningPath.find({
        "levels.0.status": {"$in": ["unlocked", "in_progress"]},
        "levels.4.status": {"$ne": "completed"}
    }, {"userId": 1}))

    emails = []
    for path in paths:
        user = User.find_one({"_id": path["userId"]}, {"email": 1})
        if user and user.get("email"):
            emails.append(user["email"])
    emails = list(set(emails))
    if write_to_file:
        write_emails_to_file(emails, "users_with_incomplete_roadmaps")
    return emails


def find_users_without_interviews(write_to_file=False):
    interviewed_ids = Interview.distinct("user_id")
    users = list(User.find({"_id": {"$nin": interviewed_ids}}, {"email": 1}))
    emails = [u["email"] for u in users if u.get("email")]
    if write_to_file:
        write_emails_to_file(emails, "users_without_interviews")
    return emails


def find_users_without_resumes(write_to_file=False):
    users = list(User.find({
        "$or": [
            {"resume_file_url": {"$exists": False}},
            {"resume_file_url": None},
            {"resume_file_url": ""}
        ]
    }, {"email": 1}))
    emails = [u["email"] for u in users if u.get("email")]
    if write_to_file:
        write_emails_to_file(emails, "users_without_resumes")
    return emails


def find_users_for_new_features(write_to_file=False):
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    users = list(User.find({"createdAt": {"$gte": thirty_days_ago}}, {"email": 1}))
    emails = [u["email"] for u in users if u.get("email")]
    if write_to_file:
        write_emails_to_file(emails, "users_for_new_features")
    return emails


def find_users_without_prompt_engineering(write_to_file=False):
    submission_emails = Submission.distinct("userEmail")
    users = list(User.find({"email": {"$nin": submission_emails}}, {"email": 1}))
    emails = [u["email"] for u in users if u.get("email")]
    if write_to_file:
        write_emails_to_file(emails, "users_without_prompt_engineering")
    return emails


def find_users_with_high_scores(write_to_file=False):
    users = list(User.find({"hidevs_score": {"$gte": 750}}, {"email": 1}))
    emails = [u["email"] for u in users if u.get("email")]
    if write_to_file:
        write_emails_to_file(emails, "users_with_high_scores")
    return emails


def find_users_in_talent_pool(write_to_file=False):
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    entries = list(TalentPool.find({"approved_date": {"$gte": seven_days_ago}}, {"user_id": 1}))
    emails = []
    for entry in entries:
        user = User.find_one({"_id": entry["user_id"]}, {"email": 1})
        if user and user.get("email"):
            emails.append(user["email"])
    emails = list(set(emails))
    if write_to_file:
        write_emails_to_file(emails, "users_in_talent_pool")
    return emails


def find_users_with_low_talent_scores(write_to_file=False):
    entries = list(TalentPool.find({"score": {"$lt": 60}}, {"user_id": 1}))
    emails = []
    for entry in entries:
        user = User.find_one({"_id": entry["user_id"]}, {"email": 1})
        if user and user.get("email"):
            emails.append(user["email"])
    emails = list(set(emails))
    if write_to_file:
        write_emails_to_file(emails, "users_with_low_talent_scores")
    return emails


def find_users_with_incomplete_profiles(write_to_file=False):
    users = list(User.find({
        "$or": [
            {"full_name": {"$exists": False}},
            {"full_name": None},
            {"full_name": ""},
            {"linkedin_profile_url": {"$exists": False}},
            {"linkedin_profile_url": None},
            {"linkedin_profile_url": ""},
            {"resume_file_url": {"$exists": False}},
            {"resume_file_url": None},
            {"resume_file_url": ""},
            {"github_url": {"$exists": False}},
            {"github_url": None},
            {"github_url": ""}
        ]
    }, {"email": 1}))
    emails = [u["email"] for u in users if u.get("email")]
    if write_to_file:
        write_emails_to_file(emails, "users_with_incomplete_profiles")
    return emails


# Function to fetch cohort emails from external API
def get_cohort_emails():
    """Fetch cohort emails from the cohort API endpoint."""
    url = os.getenv("COHORT_API_URL", "http://localhost:5000/api/cohort/admin/cohort-emails")
    admin_token = os.getenv("ADMIN_TOKEN")
    if not admin_token:
        raise ValueError("ADMIN_TOKEN not set in environment variables.")
    
    headers = {
        "Cookie": f"adminToken={admin_token}"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["emails"]


# -------------------------
# Main Runner
# -------------------------

def main():
    print("Starting user event tracking...")
    find_users_with_unsubmitted_projects(write_to_file=True)
    find_users_with_incomplete_enrollments(write_to_file=True)
    find_users_close_to_completing_courses(write_to_file=True)
    find_users_with_unstarted_roadmaps(write_to_file=True)
    find_users_with_incomplete_roadmaps(write_to_file=True)
    find_users_without_interviews(write_to_file=True)
    find_users_without_resumes(write_to_file=True)
    find_users_for_new_features(write_to_file=True)
    find_users_without_prompt_engineering(write_to_file=True)
    find_users_with_high_scores(write_to_file=True)
    find_users_in_talent_pool(write_to_file=True)
    find_users_with_low_talent_scores(write_to_file=True)
    find_users_with_incomplete_profiles(write_to_file=True)
    print("All user events tracked and saved to output directory.")
    client.close()


if __name__ == "__main__":
    try:
        print("Sample project:", Project.find_one())
        print("Sample user:", User.find_one())
        main()
    except Exception as e:
        print("Error in main function:", str(e))
        sys.exit(1)
