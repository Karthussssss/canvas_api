from abc import ABC, abstractmethod
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List
from utils.error_handler import handle_api_error

class BaseCollector(ABC):
    def __init__(self, student_name: str, api_key: str, domain: str, user_id: int):
        self.student_name = student_name
        self.api_key = api_key
        self.domain = domain
        self.user_id = user_id
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.base_url = f"https://{self.domain}/api/v1"

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Make a request to Canvas API matching canvas_grade.py"""
        url = f"{self.base_url}/{endpoint}"
        try:
            print(f"Making API request to: {url}")
            if params:
                print(f"With parameters: {params}")
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ API error: {response.status_code} for {url}")
                return None
                
        except Exception as e:
            print(f"⚠️ Request error: {str(e)} for {url}")
            return None

    def get_student_name(self) -> str:
        """Get student name from Canvas API matching canvas_grade.py"""
        # Use exact same endpoint as in canvas_grade.py
        url = "users/self/profile"
        response = self._make_request(url)
        if response:
            return response.get("name", "Unknown Student")
        return "Unknown Student"

    @abstractmethod
    def collect(self) -> List[Dict[str, Any]]:
        """Collect data from Canvas API"""
        pass

    def get_timestamp(self) -> str:
        """Get current timestamp in required format"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
