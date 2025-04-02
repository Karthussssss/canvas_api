import requests
import time
from typing import Dict, List, Optional, Any
from data_collectors.base_collector import BaseCollector
from config import COURSE_NAME_TO_CHINESE, STUDENT_TO_CHINESE_NAME, STUDENT_TO_PREFERRED_ENGLISH_NAME, convert_score_to_grade

class GradesCollector(BaseCollector):
    def get_enrolled_courses(self) -> List[Dict]:
        """Get all courses the student is enrolled in"""
        url = "courses"
        params = {
            "enrollment_state": "active",
            "include": ["total_scores"]
        }
        data = self._make_request(url, params)
        
        # Filter for courses with valid enrollments 
        if data:
            # Only include courses where the user is actually enrolled and has grades
            return [
                course for course in data 
                if course.get("enrollments") and self.is_2025s_course(course.get("name", ""))
            ]
        return []

    def is_2025s_course(self, course_name: str) -> bool:
        """Check if the course is from Spring 2025 (2025S)"""
        return "(2025S-" in course_name

    def collect(self) -> List[Dict[str, Any]]:
        """Collect grades data for all enrolled courses"""
        grades_data = []
        timestamp = self.get_timestamp()
        
        # Get student name to match working example
        canvas_student_name = self.get_student_name()
        print(f"📢 Student: {canvas_student_name}")
        
        # Get the correct Chinese and English names
        student_cn_name = STUDENT_TO_CHINESE_NAME.get(canvas_student_name, "")
        student_en_name = STUDENT_TO_PREFERRED_ENGLISH_NAME.get(canvas_student_name, "")
        
        print(f"Student Chinese Name: {student_cn_name}")
        print(f"Student English Name: {student_en_name}")
        
        # Get enrolled courses directly with grades
        enrolled_courses = self.get_enrolled_courses()
        
        if not enrolled_courses:
            print(f"⚠️ No active course enrollments found for {canvas_student_name}")
            return grades_data
            
        print(f"Found {len(enrolled_courses)} active Spring 2025 course enrollments.")
        
        for course in enrolled_courses:
            course_name_en = course["name"]
            course_name_cn = COURSE_NAME_TO_CHINESE.get(course_name_en, "未知课程")
            
            # Get grade directly from enrollment data
            enrollments = course.get("enrollments", [])
            if enrollments and len(enrollments) > 0:
                # Get the first enrollment's grade
                enrollment = enrollments[0]
                current_score = enrollment.get("computed_current_score")
                if current_score is None:
                    # Try alternate grade field if available
                    current_score = enrollment.get("current_score")
                
                # If still no score, check grades object
                if current_score is None and "grades" in enrollment:
                    current_score = enrollment["grades"].get("current_score")
                
                # Convert to string for consistency
                score = str(current_score) if current_score is not None else "N/A"
            else:
                score = "N/A"
            
            # Convert score to grade
            grade = convert_score_to_grade(score)
            
            print(f"\nProcessing grade for {course_name_cn} ({course_name_en})...")
            print(f"✅ Course: {course_name_cn} ({course_name_en}) | Score: {score}")
            
            grades_data.append({
                "student_name": canvas_student_name,
                "student_chinese_name": student_cn_name,
                "student_english_name": student_en_name,
                "course_name": course_name_en,
                "course_name_chinese": course_name_cn,
                "score": score,
                "grade": grade,
                "fetch_time": timestamp
            })
            
        return grades_data
