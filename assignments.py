#!/usr/bin/env python3
import requests
import json
import os
import sys
from datetime import datetime

# Hardcoded credentials - can be filled in directly here
HARDCODED_CREDENTIALS = {
    "api_key": "123123",  # e.g. "123123"
    "domain": "",   # e.g. "shastacollege.instructure.com"
    "user_id": ""   # e.g. "72642"
}

# Get credentials either from hardcoded values, user input, or file
def get_credentials():
    # Check if hardcoded credentials are filled in
    if HARDCODED_CREDENTIALS["api_key"] and HARDCODED_CREDENTIALS["domain"] and HARDCODED_CREDENTIALS["user_id"]:
        print("✅ Using hardcoded credentials")
        return HARDCODED_CREDENTIALS
    
    # Ask user if they want to input credentials
    print("No hardcoded credentials found. Please choose an option:")
    print("1. Enter credentials manually")
    print("2. Load from credentials.json file")
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        api_key = input("Enter Canvas API key: ")
        domain = input("Enter Canvas domain (e.g., shastacollege.instructure.com): ")
        user_id = input("Enter Canvas user ID: ")
        
        return {
            "api_key": api_key,
            "domain": domain,
            "user_id": user_id
        }
    else:
        # Try to load from file
        try:
            return load_credentials_from_file()
        except Exception as e:
            print(f"❌ Error loading credentials: {str(e)}")
            print("Switching to manual entry...")
            
            api_key = input("Enter Canvas API key: ")
            domain = input("Enter Canvas domain (e.g., shastacollege.instructure.com): ")
            user_id = input("Enter Canvas user ID: ")
            
            return {
                "api_key": api_key,
                "domain": domain,
                "user_id": user_id
            }

# Load credentials from JSON file (alternative method)
def load_credentials_from_file():
    credentials_file = "config/credentials.json"
    if not os.path.exists(credentials_file):
        raise FileNotFoundError(f"Credentials file not found: {credentials_file}")
        
    with open(credentials_file, 'r') as f:
        credentials = json.load(f)
    
    # Get Peter Deng's credentials if available
    peter_credentials = credentials.get("Deng Caihaoxuan")
    if peter_credentials:
        return peter_credentials
        
    # If no specific student found, ask user to select one
    print("Available students:")
    students = list(credentials.keys())
    for i, student in enumerate(students):
        print(f"{i+1}. {student}")
    
    selection = int(input("Select a student (number): ")) - 1
    if 0 <= selection < len(students):
        return credentials[students[selection]]
    else:
        raise ValueError("Invalid selection")

# Get Music Appreciation course ID or ask for course name
def get_course_id(api_key, domain, course_name=None):
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"https://{domain}/api/v1/courses"
    params = {
        "enrollment_state": "active",
        "include": ["total_scores"]
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        courses = response.json()
        
        # If course name specified, search for it
        if course_name:
            for course in courses:
                if course_name.lower() in course.get("name", "").lower():
                    return course.get("id")
            return None
        
        # Otherwise show all courses and let user pick
        print("\nAvailable courses:")
        for i, course in enumerate(courses):
            print(f"{i+1}. {course.get('name', 'Unknown')}")
        
        selection = int(input("Select a course (number): ")) - 1
        if 0 <= selection < len(courses):
            return courses[selection].get("id")
    
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
            if str(entry.get("user_id")) == str(user_id):
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
    print("=" * 60)
    print("Canvas Assignment Status Checker")
    print("=" * 60)
    
    # Get credentials
    credentials = get_credentials()
    
    if not credentials:
        print("❌ Could not get valid credentials")
        return
    
    api_key = credentials.get("api_key")
    domain = credentials.get("domain")
    user_id = credentials.get("user_id")
    
    if not api_key or not domain or not user_id:
        print("❌ Missing required credentials")
        return
    
    print(f"✅ Using credentials for user ID: {user_id}")
    
    # Ask if user wants to check Music Appreciation or other course
    print("\nDo you want to check:")
    print("1. Music Appreciation")
    print("2. Enter a different course name")
    print("3. Show all courses")
    course_choice = input("Enter your choice (1, 2, or a3): ")
    
    if course_choice == "1":
        course_id = get_course_id(api_key, domain, "Music Appreciation")
    elif course_choice == "2":
        course_name = input("Enter course name to search: ")
        course_id = get_course_id(api_key, domain, course_name)
    else:
        course_id = get_course_id(api_key, domain)
    
    if not course_id:
        print("❌ Could not find course")
        return
    
    print(f"✅ Found course (Course ID: {course_id})")
    
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

    # Ask if user wants to save results to a file
    save_choice = input("\nDo you want to save results to a file? (y/n): ")
    if save_choice.lower() == 'y':
        filename = input("Enter filename (default: assignment_status.txt): ") or "assignment_status.txt"
        with open(filename, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("Canvas Assignment Status Report\n")
            f.write("=" * 60 + "\n\n")
            
            if assignments:
                f.write("=== Assignments Status ===\n")
                f.write("Name | Due Date | Status | Score\n")
                f.write("-" * 60 + "\n")
                
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
                    
                    f.write(f"{name} | {due_date} | {status} | {score}\n")
                
                f.write("\n")
            
            if quizzes:
                f.write("=== Quizzes Status ===\n")
                f.write("Name | Due Date | Status | Score\n")
                f.write("-" * 60 + "\n")
                
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
                    
                    f.write(f"{name} | {due_date} | {status} | {score}\n")
                
                f.write("\n")
            
            if discussions:
                f.write("=== Discussions Status ===\n")
                f.write("Name | Due Date | Status\n")
                f.write("-" * 60 + "\n")
                
                for discussion in discussions:
                    discussion_id = discussion.get("id")
                    name = discussion.get("title")
                    due_date = format_date(discussion.get("due_at"))
                    
                    participation = get_discussion_participation(api_key, domain, course_id, discussion_id, user_id)
                    
                    status = "Participated" if participation["participated"] else "Not Participated"
                    
                    f.write(f"{name} | {due_date} | {status}\n")
            
            print(f"✅ Results saved to {filename}")

if __name__ == "__main__":
    main()