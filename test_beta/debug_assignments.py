import requests
import json
import csv
import os
from datetime import datetime

# API credentials and settings
ACCESS_TOKEN = "5495~HeUC3AawWTLy3Gf3Lf92xW9ew9tAJYGXwzVXGGT8u9fyELhuWBM3LcVPu3JYaHLe"
CANVAS_DOMAIN = "shastacollege.instructure.com"
USER_ID = 77632
HEADERS = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
OUTPUT_CSV = "canvas_assignments.csv"

def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=4, ensure_ascii=False))

def print_table(headers, data, column_widths=None):
    """Print a simple ASCII table"""
    if not column_widths:
        # Calculate column widths
        column_widths = [len(h) for h in headers]
        for row in data:
            for i, item in enumerate(row):
                column_widths[i] = max(column_widths[i], len(str(item)))
    
    # Print headers
    header_line = " | ".join(h.ljust(column_widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print("-" * len(header_line))
    
    # Print data
    for row in data:
        print(" | ".join(str(item).ljust(column_widths[i]) for i, item in enumerate(row)))

def api_call(endpoint, params=None):
    """Make an API call and return the data"""
    url = f"https://{CANVAS_DOMAIN}/api/v1/{endpoint}"
    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {url}")
    else:
        print(f"Error {response.status_code} from {url}: {response.text}")
    
    return None

def get_courses():
    """Get all active courses"""
    print("\n===== FETCHING COURSES =====")
    courses = api_call("courses", {"enrollment_state": "active"})
    
    if courses:
        print(f"Found {len(courses)} courses")
        course_data = []
        for i, course in enumerate(courses):
            course_data.append([i+1, course.get('name'), course.get('id')])
        
        print_table(["#", "Course Name", "ID"], course_data)
    
    return courses

def get_assignments(course_id):
    """Get all assignments for a course"""
    return api_call(f"courses/{course_id}/assignments")

def get_submissions(course_id, assignment_id):
    """Get submission for an assignment"""
    return api_call(f"courses/{course_id}/assignments/{assignment_id}/submissions/{USER_ID}")

def format_date(date_str):
    """Format a date string or return a default"""
    if not date_str or date_str == "No due date":
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return date_str

def get_assignment_data(courses):
    """Get assignment data for all courses"""
    all_assignments = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for course in courses:
        course_id = course["id"]
        course_name = course["name"]
        
        print(f"\n\n===== RETRIEVING ASSIGNMENTS FOR: {course_name} =====")
        
        assignments = get_assignments(course_id)
        if not assignments:
            print(f"No assignments found for {course_name}")
            continue
        
        print(f"Found {len(assignments)} assignments")
        
        course_assignments = []
        for assignment in assignments:
            assignment_id = assignment["id"]
            assignment_name = assignment["name"]
            due_date = format_date(assignment.get("due_at"))
            points_possible = assignment.get("points_possible", 0)
            
            # Get submission data
            submission = get_submissions(course_id, assignment_id)
            
            submitted_date = "Not submitted"
            grade = "N/A"
            score = "N/A"
            status = "Not submitted"
            
            if submission:
                submitted = submission.get("submitted_at")
                if submitted:
                    submitted_date = format_date(submitted)
                
                if submission.get("grade"):
                    grade = submission["grade"]
                
                if submission.get("score") is not None:
                    score = submission["score"]
                
                status = submission.get("workflow_state", "unknown")
            
            # Add to course assignments
            course_assignments.append([
                assignment_name,
                course_name,
                due_date,
                points_possible,
                submitted_date,
                grade,
                score,
                status,
                timestamp
            ])
        
        # Display table for this course
        headers = ["Assignment", "Due Date", "Points", "Submitted", "Grade", "Score", "Status"]
        table_data = [[a[0], a[2], a[3], a[4], a[5], a[6], a[7]] for a in course_assignments]
        print_table(headers, table_data)
        
        # Add to all assignments
        all_assignments.extend(course_assignments)
    
    return all_assignments

def save_to_csv(assignments_data):
    """Save assignments data to CSV"""
    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "作业名称", "课程名称", "截止日期", "总分", 
            "提交日期", "评分", "得分", "状态", "抓取时间"
        ])
        writer.writerows(assignments_data)
    
    print(f"\n✅ 作业数据已保存到 {os.path.abspath(OUTPUT_CSV)}")

if __name__ == "__main__":
    courses = get_courses()
    
    if courses:
        assignments_data = get_assignment_data(courses)
        save_to_csv(assignments_data) 