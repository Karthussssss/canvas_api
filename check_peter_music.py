#!/usr/bin/env python3
import requests
import json
import os
from datetime import datetime

# Load credentials
def load_credentials():
    credentials_file = "config/credentials.json"
    with open(credentials_file, 'r') as f:
        return json.load(f)

# Get Peter Deng's credentials
def get_peter_credentials():
    credentials = load_credentials()
    # Peter's name in the credentials file is "Deng Caihaoxuan"
    return credentials.get("Deng Caihaoxuan")

# Get Music Appreciation course ID
def get_music_appreciation_course_id(api_key, domain):
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"https://{domain}/api/v1/courses"
    params = {
        "enrollment_state": "active",
        "include": ["total_scores"]
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        courses = response.json()
        for course in courses:
            if "Music Appreciation" in course.get("name", ""):
                return course.get("id")
    
    return None

# Get assignments for a course
def get_assignments(api_key, domain, course_id):
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"https://{domain}/api/v1/courses/{course_id}/assignments"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    
    return []

# Get quizzes for a course
def get_quizzes(api_key, domain, course_id):
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"https://{domain}/api/v1/courses/{course_id}/quizzes"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    
    return []

# Get discussions for a course
def get_discussions(api_key, domain, course_id):
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"https://{domain}/api/v1/courses/{course_id}/discussion_topics"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    
    return []

# Get submission status for assignments
def get_submission_status(api_key, domain, course_id, assignment_id, user_id):
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"https://{domain}/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    
    return None

# Get quiz submission status
def get_quiz_submission_status(api_key, domain, course_id, quiz_id, user_id):
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"https://{domain}/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions"
    params = {"user_id": user_id}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data and "quiz_submissions" in data and data["quiz_submissions"]:
            return data["quiz_submissions"][0]
    
    return None

# Get discussion participation status
def get_discussion_participation(api_key, domain, course_id, discussion_id, user_id):
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"https://{domain}/api/v1/courses/{course_id}/discussion_topics/{discussion_id}/entries"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        entries = response.json()
        # Check if user has participated
        for entry in entries:
            if entry.get("user_id") == user_id:
                return {"participated": True, "entry": entry}
    
    return {"participated": False, "entry": None}

def format_date(date_str):
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
            return date_obj.strftime("%Y-%m-%d")
        except:
            return "N/A"
    return "No due date"

def main():
    # Get Peter's credentials
    peter_credentials = get_peter_credentials()
    
    if not peter_credentials:
        print("❌ Could not find Peter Deng's credentials")
        return
    
    api_key = peter_credentials.get("api_key")
    domain = peter_credentials.get("domain")
    user_id = peter_credentials.get("user_id")
    
    if not api_key or not domain or not user_id:
        print("❌ Missing required credentials for Peter Deng")
        return
    
    print(f"✅ Found Peter Deng's credentials (User ID: {user_id})")
    
    # Get Music Appreciation course ID
    course_id = get_music_appreciation_course_id(api_key, domain)
    
    if not course_id:
        print("❌ Could not find Music Appreciation course")
        return
    
    print(f"✅ Found Music Appreciation course (Course ID: {course_id})")
    
    # Get assignments, quizzes, and discussions
    assignments = get_assignments(api_key, domain, course_id)
    quizzes = get_quizzes(api_key, domain, course_id)
    discussions = get_discussions(api_key, domain, course_id)
    
    total_items = len(assignments) + len(quizzes) + len(discussions)
    print(f"✅ Found {len(assignments)} assignments, {len(quizzes)} quizzes, and {len(discussions)} discussions")
    
    # Print Assignments
    if assignments:
        print("\n=== Assignments Status ===")
        print("Name | Due Date | Status | Score")
        print("-" * 60)
        
        for assignment in assignments:
            assignment_id = assignment.get("id")
            name = assignment.get("name")
            due_date = format_date(assignment.get("due_at"))
            
            submission = get_submission_status(api_key, domain, course_id, assignment_id, user_id)
            
            if submission:
                status = submission.get("workflow_state", "unknown")
                score = submission.get("score")
                
                # Format status
                if status == "submitted":
                    status = "Submitted"
                elif status == "graded":
                    status = "Graded"
                elif status == "pending_review":
                    status = "Pending Review"
                elif status == "unsubmitted":
                    status = "Not Submitted"
                
                # Format score
                if score is not None:
                    score = f"{score}/{assignment.get('points_possible', 'N/A')}"
                else:
                    score = "N/A"
            else:
                status = "Unknown"
                score = "N/A"
            
            print(f"{name} | {due_date} | {status} | {score}")
    
    # Print Quizzes
    if quizzes:
        print("\n=== Quizzes Status ===")
        print("Name | Due Date | Status | Score")
        print("-" * 60)
        
        for quiz in quizzes:
            quiz_id = quiz.get("id")
            name = quiz.get("title")
            due_date = format_date(quiz.get("due_at"))
            
            submission = get_quiz_submission_status(api_key, domain, course_id, quiz_id, user_id)
            
            if submission:
                status = submission.get("workflow_state", "unknown")
                score = submission.get("score")
                
                # Format status
                if status == "complete":
                    status = "Completed"
                elif status == "pending_review":
                    status = "Pending Review"
                elif status == "untaken":
                    status = "Not Taken"
                
                # Format score
                if score is not None:
                    score = f"{score}/{quiz.get('points_possible', 'N/A')}"
                else:
                    score = "N/A"
            else:
                status = "Not Started"
                score = "N/A"
            
            print(f"{name} | {due_date} | {status} | {score}")
    
    # Print Discussions
    if discussions:
        print("\n=== Discussions Status ===")
        print("Name | Due Date | Status")
        print("-" * 60)
        
        for discussion in discussions:
            discussion_id = discussion.get("id")
            name = discussion.get("title")
            due_date = format_date(discussion.get("due_at"))
            
            participation = get_discussion_participation(api_key, domain, course_id, discussion_id, user_id)
            
            status = "Participated" if participation["participated"] else "Not Participated"
            
            print(f"{name} | {due_date} | {status}")

if __name__ == "__main__":
    main() 