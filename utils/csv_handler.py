import csv
import os
from typing import List, Dict, Any
from utils.error_handler import handle_file_error

class CSVHandler:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Ensure the directory for the CSV file exists"""
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def save_grades(self, data: List[Dict[str, Any]], append: bool = True) -> None:
        """Save grades data to CSV file"""
        fieldnames = [
            "student_name", "student_chinese_name", "student_english_name",
            "course_name", "course_name_chinese", "score", "grade", "fetch_time"
        ]

        try:
            # Check if file exists and has data
            file_exists = os.path.exists(self.file_path) and os.path.getsize(self.file_path) > 0
            
            mode = 'a' if append and file_exists else 'w'
            
            with open(self.file_path, mode, newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                # Write header only for new files
                if mode == 'w':
                    writer.writeheader()
                
                writer.writerows(data)
                
            print(f"✅ Successfully saved {len(data)} records to {self.file_path}")
            
        except Exception as e:
            handle_file_error(self.file_path, "write", e)
