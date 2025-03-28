import json
import os
import requests
from typing import Dict, Optional
from utils.error_handler import handle_api_error, handle_credentials_error

class CredentialManager:
    def __init__(self, credentials_file: str = "credentials.json"):
        self.credentials_file = credentials_file
        self.credentials = self._load_credentials()

    def _load_credentials(self) -> Dict:
        """Load credentials from JSON file"""
        try:
            if not os.path.exists(self.credentials_file):
                print(f"Warning: {self.credentials_file} not found. Creating new file...")
                self._save_credentials({})
                return {}
                
            with open(self.credentials_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    print(f"Warning: {self.credentials_file} is empty. Creating new file...")
                    self._save_credentials({})
                    return {}
                return json.loads(content)
                
        except json.JSONDecodeError as e:
            print(f"Error: {self.credentials_file} is not valid JSON. Please check the file format.")
            raise
        except Exception as e:
            handle_credentials_error("system", e)
            return {}

    def _save_credentials(self, data: Dict = None) -> None:
        """Save credentials to JSON file"""
        try:
            if data is None:
                data = self.credentials
            with open(self.credentials_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            handle_credentials_error("system", e)

    def get_user_id(self, student_name: str) -> Optional[int]:
        """Get user ID from Canvas API using student's profile"""
        try:
            student = self.credentials.get(student_name)
            if not student:
                raise ValueError(f"No credentials found for student: {student_name}")

            api_key = student.get("api_key")
            domain = student.get("domain")
            
            if not api_key or not domain:
                raise ValueError(f"Missing API key or domain for student: {student_name}")

            headers = {"Authorization": f"Bearer {api_key}"}
            url = f"https://{domain}/api/v1/users/self/profile"
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                # Get the Canvas student name
                canvas_name = response.json().get("name")
                # Update the student's Canvas name in credentials
                if canvas_name and student.get("student_name") != canvas_name:
                    student["student_name"] = canvas_name
                    self._save_credentials()
                    print(f"Updated Canvas name for {student_name}: {canvas_name}")
                
                return response.json().get("id")
            else:
                handle_api_error(student_name, "profile", Exception(f"API returned status code: {response.status_code}"))
                return None
                
        except Exception as e:
            handle_api_error(student_name, "profile", e)
            return None

    def update_missing_user_ids(self) -> None:
        """Update missing user IDs for all students"""
        if not self.credentials:
            print("No student credentials found. Please add student credentials first.")
            return
            
        for student_name in self.credentials:
            student = self.credentials[student_name]
            if not student.get("user_id"):
                user_id = self.get_user_id(student_name)
                if user_id:
                    student["user_id"] = user_id
                    print(f"Updated user ID for {student_name}: {user_id}")
                else:
                    print(f"Failed to get user ID for {student_name}")
        
        self._save_credentials()

    def get_student_credentials(self, student_name: str) -> Optional[Dict]:
        """Get credentials for a specific student"""
        return self.credentials.get(student_name)

    def get_all_student_names(self) -> list:
        """Get list of all student names"""
        return list(self.credentials.keys()) 