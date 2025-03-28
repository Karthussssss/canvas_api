from typing import Dict, Any, List
from .base_collector import BaseCollector
from config import COURSE_NAME_TO_CHINESE, STUDENT_TO_CHINESE_NAME, STUDENT_TO_PREFERRED_ENGLISH_NAME, convert_score_to_grade

class GradesCollector(BaseCollector):
    def get_courses(self) -> List[Dict]:
        """Get all enrolled courses"""
        # Using the exact API call from canvas_grade.py
        url = "courses"
        data = self._make_request(url)
        return data if data else []

    def get_course_grades(self, course_id: int) -> str:
        """Get course grades for a specific course"""
        # Using the exact API call from canvas_grade.py
        url = f"courses/{course_id}/enrollments"
        data = self._make_request(url)
        
        if not data:
            return "N/A"
            
        for enrollment in data:
            # Important: Look for the exact user_id match as in canvas_grade.py
            if enrollment["user_id"] == self.user_id and "grades" in enrollment:
                return enrollment["grades"].get("current_score", "N/A")
        return "N/A"
        
    def is_2025s_course(self, course_name: str) -> bool:
        """Check if the course is from Spring 2025 (2025S)"""
        return "(2025S-" in course_name

    def collect(self) -> List[Dict[str, Any]]:
        """Collect grades data for all courses"""
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
        
        # Get courses
        courses = self.get_courses()
        
        if not courses:
            print(f"⚠️ No courses found for {canvas_student_name}")
            return grades_data
            
        # Filter for 2025S courses only
        spring_2025_courses = [course for course in courses if self.is_2025s_course(course["name"])]
        
        print(f"Found {len(spring_2025_courses)} Spring 2025 courses out of {len(courses)} total courses.")
        
        for course in spring_2025_courses:
            course_name_en = course["name"]
            course_name_cn = COURSE_NAME_TO_CHINESE.get(course_name_en, "未知课程")
            course_id = course["id"]
            
            print(f"\nGetting grades for {course_name_cn} ({course_name_en})...")
            score = self.get_course_grades(course_id)
            
            # Convert score to grade
            grade = convert_score_to_grade(score)
            
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
            
            print(f"✅ Course: {course_name_cn} ({course_name_en}) | Score: {score}%")
            
        return grades_data
