from fastapi import FastAPI
from typing import List
import api  # import your existing query logic

app = FastAPI()

@app.get("/api/user-retention/emails/users_with_unsubmitted_projects", response_model=List[str])
def get_users_with_unsubmitted_projects():
    return api.find_users_with_unsubmitted_projects()

@app.get("/api/user-retention/emails/users_with_incomplete_courses", response_model=List[str])
def get_users_with_incomplete_enrollments():
    return api.find_users_with_incomplete_enrollments()

@app.get("/api/user-retention/emails/users_close_to_completing_courses", response_model=List[str])
def get_users_close_to_completing_courses():
    return api.find_users_close_to_completing_courses()

@app.get("/api/user-retention/emails/users_with_unstarted_roadmaps", response_model=List[str])
def get_users_with_unstarted_roadmaps():
    return api.find_users_with_unstarted_roadmaps()

@app.get("/api/user-retention/emails/users_with_incomplete_roadmaps", response_model=List[str])
def get_users_with_incomplete_roadmaps():
    return api.find_users_with_incomplete_roadmaps()

@app.get("/api/user-retention/emails/users_without_interviews", response_model=List[str])
def get_users_without_interviews():
    return api.find_users_without_interviews()

@app.get("/api/user-retention/emails/users_without_resumes", response_model=List[str])
def get_users_without_resumes():
    return api.find_users_without_resumes()

@app.get("/api/user-retention/emails/users_for_new_features", response_model=List[str])
def get_users_for_new_features():
    return api.find_users_for_new_features()

@app.get("/api/user-retention/emails/users_without_prompt_engineering", response_model=List[str])
def get_users_without_prompt_engineering():
    return api.find_users_without_prompt_engineering()

@app.get("/api/user-retention/emails/users_with_high_scores", response_model=List[str])
def get_users_with_high_scores():
    return api.find_users_with_high_scores()

@app.get("/api/user-retention/emails/users_in_talent_pool", response_model=List[str])
def get_users_in_talent_pool():
    return api.find_users_in_talent_pool()

@app.get("/api/user-retention/emails/users_with_low_talent_scores", response_model=List[str])
def get_users_with_low_talent_scores():
    return api.find_users_with_low_talent_scores()

@app.get("/api/user-retention/emails/users_with_incomplete_profiles", response_model=List[str])
def get_users_with_incomplete_profiles():
    return api.find_users_with_incomplete_profiles()
