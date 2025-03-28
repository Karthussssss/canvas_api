import requests
import json

# API credentials and settings
ACCESS_TOKEN = "5495~HeUC3AawWTLy3Gf3Lf92xW9ew9tAJYGXwzVXGGT8u9fyELhuWBM3LcVPu3JYaHLe"
CANVAS_DOMAIN = "shastacollege.instructure.com"
USER_ID = 77632
HEADERS = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=4, ensure_ascii=False))

def debug_api_call(endpoint, params=None):
    """Make an API call and print the raw response"""
    url = f"https://{CANVAS_DOMAIN}/api/v1/{endpoint}"
    print(f"\n🔍 Debug API Call: {url}")
    
    response = requests.get(url, headers=HEADERS, params=params)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("\nRaw Response:")
            print_json(data)
            return data
        except json.JSONDecodeError:
            print("Response is not JSON decodable")
            print(response.text)
    else:
        print(f"Error: {response.text}")
    
    return None

if __name__ == "__main__":
    # Debug profile data
    print("\n===== USER PROFILE =====")
    debug_api_call("users/self/profile")
    
    # Debug courses data
    print("\n===== COURSES DATA =====")
    courses = debug_api_call("courses")
    
    # Debug enrollments for a specific course
    if courses and len(courses) > 0:
        course_id = courses[0]["id"]
        course_name = courses[0]["name"]
        print(f"\n===== ENROLLMENTS FOR COURSE: {course_name} =====")
        debug_api_call(f"courses/{course_id}/enrollments") 