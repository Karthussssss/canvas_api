import os
import json
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Path to credentials file (stored outside version control)
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "credentials.json")

# Function to load all student credentials
def load_student_credentials():
    """Load student credentials from JSON file"""
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(f"Credentials file not found: {CREDENTIALS_FILE}")
    
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in credentials file: {CREDENTIALS_FILE}")
    except Exception as e:
        raise Exception(f"Error loading credentials: {str(e)}")

# Load student credentials
try:
    STUDENT_CREDENTIALS = load_student_credentials()
except Exception as e:
    logging.error(f"Failed to load credentials: {str(e)}")
    STUDENT_CREDENTIALS = {}

# Function to get API headers for a specific student
def get_headers_for_student(student_id):
    """Get API headers with token for a specific student"""
    if student_id not in STUDENT_CREDENTIALS:
        raise ValueError(f"No credentials found for student ID: {student_id}")
        
    credentials = STUDENT_CREDENTIALS[student_id]
    api_key = credentials.get("api_key")
    
    if not api_key:
        raise ValueError(f"Missing API key for student ID: {student_id}")
        
    return {"Authorization": f"Bearer {api_key}"}

# Function to get domain for a specific student
def get_domain_for_student(student_id):
    """Get Canvas domain for a specific student"""
    if student_id not in STUDENT_CREDENTIALS:
        raise ValueError(f"No credentials found for student ID: {student_id}")
        
    credentials = STUDENT_CREDENTIALS[student_id]
    domain = credentials.get("domain")
    
    if not domain:
        raise ValueError(f"Missing domain for student ID: {student_id}")
        
    return domain

# Function to get user ID for a specific student
def get_user_id_for_student(student_id):
    """Get Canvas user ID for a specific student"""
    if student_id not in STUDENT_CREDENTIALS:
        raise ValueError(f"No credentials found for student ID: {student_id}")
        
    credentials = STUDENT_CREDENTIALS[student_id]
    user_id = credentials.get("user_id")
    
    if not user_id:
        raise ValueError(f"Missing user ID for student ID: {student_id}")
    
    try:
        return int(user_id)
    except ValueError:
        raise ValueError(f"User ID must be a valid integer for student ID: {student_id}")

# Student Name Mappings (from credentials.json)
def build_student_mappings():
    student_to_chinese = {}
    student_to_english = {}
    
    for student_name, data in STUDENT_CREDENTIALS.items():
        # Canvas API name to Chinese name
        canvas_name = data.get("student_name", student_name)
        chinese_name = data.get("student_chinese_name", "")
        english_name = data.get("student_english_name", "")
        
        if canvas_name:
            student_to_chinese[canvas_name] = chinese_name
            student_to_english[canvas_name] = english_name
    
    return student_to_chinese, student_to_english

STUDENT_TO_CHINESE_NAME, STUDENT_TO_PREFERRED_ENGLISH_NAME = build_student_mappings()

# Course Mappings (from canvas_grade.py)
COURSE_NAME_TO_CHINESE = {
    "Calculus 3A - S9723 (2025S-MATH-3A)": "微积分 3A",
    "General Biology - S9768 (2025S-BIOL-10)": "生物学",
    "General Psychology - S9987 (2025S-PSYC-1A)": "心理学",
    "Music Appreciation - S8262 (2025S-MUS-10)": "音乐鉴赏",
    "Precalculus - F9621 (2024F-MATH-2)": "预微积分",
    "Principles of Economics-Micro - S0031 (2025S-ECON-1A)": "微观经济学导论"
}

COURSE_TO_ACADEMIC_SUPPORT = {
    # Example: "Calculus 3A - S9723 (2025S-MATH-3A)": "Kathy Li",
    # Example: "General Biology - S9768 (2025S-BIOL-10)": "John Smith",
}

# Grade Mapping
def convert_score_to_grade(score):
    """Convert numerical score to letter grade"""
    if score is None or score == "N/A":
        return "N/A"
    
    try:
        score = float(score)
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    except (ValueError, TypeError):
        return "N/A"

# CSV File Configuration
GRADES_CSV_PATH = os.path.join("data", "grades.csv")
ASSIGNMENTS_CSV_PATH = os.path.join("data", "assignments.csv")
