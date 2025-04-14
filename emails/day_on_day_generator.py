#!/usr/bin/env python3
"""
Day-on-Day Performance Report Generator
Generates HTML reports that show day-on-day changes in student performance
"""

import os
import pandas as pd
import jinja2
from datetime import datetime
import base64
from pathlib import Path
import json
import numpy as np
from typing import List, Dict, Any, Union, Tuple
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Color codes for progress bars
GREEN = "#4CAF50"  # >70% A grades
ORANGE = "#FF9800"  # 30-70% A grades
RED = "#F44336"     # <30% A grades

def get_grade_class(score: float) -> str:
    """Return CSS class based on grade score"""
    if score >= 90:
        return "grade-a"
    elif score >= 80:
        return "grade-b"
    else:
        return "grade-c-or-below"

def get_bar_color(percentage: float) -> str:
    """Return color for progress bar based on percentage"""
    if percentage >= 70:
        return GREEN
    elif percentage >= 30:
        return ORANGE
    else:
        return RED

def get_image_base64(image_path: str) -> str:
    """Convert image to base64 for embedding in HTML"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            # Determine the image type from the file extension
            image_type = Path(image_path).suffix.lower()[1:]  # Remove the dot and convert to lowercase
            if image_type == 'jpg':
                image_type = 'jpeg'  # Correct the MIME type for jpg
            return f"data:image/{image_type};base64,{encoded_string}"
    except Exception as e:
        logger.warning(f"Could not embed image {image_path}: {e}")
        return ""

def load_previous_data(cache_file: str) -> Dict:
    """Load previous data from cache file"""
    try:
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.warning(f"Could not load previous data: {e}")
        return {}

def save_current_data(data: Dict, cache_file: str) -> None:
    """Save current data to cache file for future comparisons"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.warning(f"Could not save current data: {e}")

def process_grades_data(grades_csv_path: str, previous_data: Dict) -> Tuple[Dict, Dict]:
    """
    Process grades data and calculate day-on-day changes
    
    Args:
        grades_csv_path: Path to CSV file with grades data
        previous_data: Dictionary with previous data for comparison
        
    Returns:
        Tuple containing current data and template context
    """
    try:
        # Read grades data
        df = pd.read_csv(grades_csv_path)
        
        # Get timestamp
        timestamp = datetime.now().strftime("%B %d, %Y - %H:%M:%S")
        date = datetime.now().strftime("%B %d, %Y")
        current_year = datetime.now().year
        
        # Get batch ID from the data
        batch_id = df["Update Batch"].iloc[0] if "Update Batch" in df.columns else "Unknown"
        
        # Count total students
        students_processed = len(df["student_name"].unique())
        students_success_rate = 100  # Assuming all students were successfully processed
        
        # Get all course columns (exclude non-course columns)
        non_course_columns = [
            "student_name", "student_chinese_name", "student_english_name", 
            "Is Latest Batch", "Updated Time", "Update Batch"
        ]
        course_columns = [col for col in df.columns if col not in non_course_columns]
        
        # Track new students (not in previous data)
        new_students = set()
        if 'students' in previous_data:
            previous_students = set(previous_data['students'])
            current_students = set(df["student_name"].unique())
            new_students = current_students - previous_students
        
        # Calculate course statistics and changes
        courses_data = []
        
        # Course to Notion page links
        COURSE_NOTION_LINKS = {
            'Calculus 3A': 'https://www.notion.so/beecominghz/Calculus-3A-S9723-2025S-MATH-3A-1c89efeede7b80a2b393f31fe9864d84?pvs=4',
            'Calculus 3B': 'https://www.notion.so/beecominghz/Calculus-3B-S9724-2025S-MATH-3B-1c89efeede7b806da355fe5786cd10f3?pvs=4',
            'Calculus 4A': 'https://www.notion.so/beecominghz/Calculus-4A-S0516-2025S-MATH-4A-1c89efeede7b80b0ab98c1b2cf18f87e?pvs=4',
            'Introduction to Statistics': 'https://www.notion.so/beecominghz/Introduction-to-Statistics-S9725-2025S-MATH-14-1c89efeede7b80e68ec6d2bf3b4961c4?pvs=4',
            'General Biology': 'https://www.notion.so/beecominghz/General-Biology-S9768-2025S-BIOL-10-1c89efeede7b80389d65fa0a81f5efca?pvs=4',
            'General Psychology': 'https://www.notion.so/beecominghz/General-Psychology-S9987-2025S-PSYC-1A-1c89efeede7b803a8173de525af2dfa0?pvs=4',
            'Introduction to Sociology': 'https://www.notion.so/beecominghz/Introduction-to-Sociology-S9999-2025S-SOC-1-1c89efeede7b80229f87e92036658383?pvs=4',
            'Principles of Economics-Micro': 'https://www.notion.so/beecominghz/Principles-of-Economics-Micro-S0031-2025S-ECON-1A-1c89efeede7b808d8f75f707eb566df1?pvs=4',
            'Introduction to Ethnic Studies': 'https://www.notion.so/beecominghz/Introduction-to-Ethnic-Studies-S9906-2025S-ETHS-1-1c89efeede7b809ba52bec16bf4d5f64?pvs=4',
            'Music Appreciation': 'https://www.notion.so/beecominghz/Music-Appreciation-S8262-2025S-MUS-10-1c89efeede7b809896d5c6ca2ae03284?pvs=4',
            'Introduction to Art': 'https://www.notion.so/beecominghz/Introduction-to-Art-S8279-2025S-ART-1-1c89efeede7b80d481a4d20ee5e8ba18?pvs=4',
            'Critical Reasoning/Read/Write': 'https://www.notion.so/beecominghz/Critical-Reasoning-Read-Write-S9853-2025S-ENGL-1C-1c89efeede7b8043ab53e6c0d592d66f?pvs=4'
        }
        
        # Store current course data for future comparisons
        current_courses = {}
        
        # Process each course
        for course in course_columns:
            # Skip known problematic courses (e.g., Precalculus)
            if course == "Precalculus":
                continue
                
            # IMPORTANT: Filter out N/A and empty values to only include enrolled students
            course_df = df[df[course] != "N/A"]
            course_df = course_df[course_df[course].notna()]
            course_df = course_df[course_df[course] != ""]
            
            # Skip if no students are taking this course
            if len(course_df) == 0:
                continue
                
            # Convert to numeric, handling potential errors
            course_df[course] = pd.to_numeric(course_df[course], errors='coerce')
            
            # Skip courses with all NaN values
            if course_df[course].isna().all():
                continue
            
            # Calculate statistics for students actually taking the course
            student_count = len(course_df)
            avg_score = course_df[course].mean()
            a_count = len(course_df[course_df[course] >= 90])
            a_grade_percent = int((a_count / student_count) * 100) if student_count > 0 else 0
            
            # Create link for course name if available
            course_name = course
            if course in COURSE_NOTION_LINKS:
                course_name = f'<a href="{COURSE_NOTION_LINKS[course]}" target="_blank" style="color: #2196F3; text-decoration: none;">{course}</a>'
            
            # Calculate day-on-day changes if previous data exists
            score_change = 0.0
            a_grade_change = 0
            
            if 'courses' in previous_data and course in previous_data['courses']:
                prev_course = previous_data['courses'][course]
                score_change = round(avg_score - prev_course['avg_score'], 1)
                a_grade_change = a_grade_percent - prev_course['a_grade_percent']
            
            # Store current course data
            current_courses[course] = {
                'student_count': student_count,
                'avg_score': avg_score,
                'a_grade_percent': a_grade_percent
            }
            
            # Add to courses_data for template
            courses_data.append({
                "name": course_name,
                "raw_name": course,  # Keep the raw name for sorting
                "student_count": student_count,
                "avg_score": f"{avg_score:.1f}",
                "score_change": f"{score_change:.1f}" if score_change != 0 else "0.0",
                "a_grade_percent": a_grade_percent,
                "a_grade_change": a_grade_change,
                "color": get_bar_color(a_grade_percent)
            })
        
        # Sort courses by A grade percentage (descending)
        courses_sorted = sorted(courses_data, key=lambda x: x["a_grade_percent"], reverse=True)
        
        # Calculate overall A grade percentage across all courses (only for enrolled students)
        total_enrollments = sum(course["student_count"] for course in courses_data)
        total_a_grades = sum(int(course["student_count"] * course["a_grade_percent"] / 100) for course in courses_data)
        a_grade_percentage = int((total_a_grades / total_enrollments) * 100) if total_enrollments > 0 else 0
        
        # Calculate overall average score across all courses
        all_scores = []
        for _, row in df.iterrows():
            for course in course_columns:
                if course == "Precalculus":  # Skip problematic courses
                    continue
                if row[course] == "N/A" or pd.isna(row[course]) or row[course] == "":
                    continue
                try:
                    score = float(row[course])
                    all_scores.append(score)
                except (ValueError, TypeError):
                    continue
        
        average_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
        
        # Calculate day-on-day changes for overall statistics
        average_score_change = 0.0
        a_grade_change = 0
        
        if 'overall' in previous_data:
            prev_overall = previous_data['overall']
            average_score_change = round(average_score - prev_overall['average_score'], 1)
            a_grade_change = a_grade_percentage - prev_overall['a_grade_percentage']
        
        # Find underperforming students (below 90%)
        underperforming_students = []
        
        for _, row in df.iterrows():
            student_name = row["student_name"]
            is_new = student_name in new_students
            
            for course in course_columns:
                if course == "Precalculus":  # Skip problematic courses
                    continue
                # Skip students not enrolled in this course
                if row[course] == "N/A" or pd.isna(row[course]) or row[course] == "":
                    continue
                    
                try:
                    score = float(row[course])
                    if score < 90:
                        needed_improvement = 90 - score
                        
                        # Calculate day-on-day changes if student was in previous data
                        score_change = 0.0
                        if 'student_scores' in previous_data and student_name in previous_data['student_scores'] and course in previous_data['student_scores'][student_name]:
                            prev_score = previous_data['student_scores'][student_name][course]
                            score_change = round(score - prev_score, 1)
                        
                        underperforming_students.append({
                            "name": student_name,
                            "course": course,
                            "score": f"{score:.1f}",
                            "grade_class": get_grade_class(score),
                            "needed_improvement": f"{needed_improvement:.1f}",
                            "score_change": score_change,
                            "is_new": is_new
                        })
                except (ValueError, TypeError):
                    # Skip non-numeric values
                    continue
        
        # Sort underperforming students by score (ascending)
        underperforming_students = sorted(underperforming_students, key=lambda x: float(x["score"]))
        
        # Find at-risk students (90-92.5%)
        at_risk_students = []
        
        for _, row in df.iterrows():
            student_name = row["student_name"]
            is_new = student_name in new_students
            
            for course in course_columns:
                if course == "Precalculus":  # Skip problematic courses
                    continue
                # Skip students not enrolled in this course
                if row[course] == "N/A" or pd.isna(row[course]) or row[course] == "":
                    continue
                    
                try:
                    score = float(row[course])
                    if 90 <= score < 92.5:
                        # Calculate day-on-day changes if student was in previous data
                        score_change = 0.0
                        if 'student_scores' in previous_data and student_name in previous_data['student_scores'] and course in previous_data['student_scores'][student_name]:
                            prev_score = previous_data['student_scores'][student_name][course]
                            score_change = round(score - prev_score, 1)
                        
                        # Check if student dropped to this level from higher score
                        is_at_risk = False
                        if 'student_scores' in previous_data and student_name in previous_data['student_scores'] and course in previous_data['student_scores'][student_name]:
                            prev_score = previous_data['student_scores'][student_name][course]
                            if prev_score >= 92.5 or score_change < 0:
                                is_at_risk = True
                        
                        at_risk_students.append({
                            "name": student_name,
                            "course": course,
                            "score": f"{score:.1f}",
                            "score_change": score_change,
                            "is_new": is_new,
                            "is_at_risk": is_at_risk
                        })
                except (ValueError, TypeError):
                    # Skip non-numeric values
                    continue
        
        # Find top performers (above 95%)
        top_performers = []
        
        for _, row in df.iterrows():
            student_name = row["student_name"]
            is_new = student_name in new_students
            
            for course in course_columns:
                if course == "Precalculus":  # Skip problematic courses
                    continue
                # Skip students not enrolled in this course
                if row[course] == "N/A" or pd.isna(row[course]) or row[course] == "":
                    continue
                    
                try:
                    score = float(row[course])
                    if score >= 95:
                        # Calculate day-on-day changes if student was in previous data
                        score_change = 0.0
                        if 'student_scores' in previous_data and student_name in previous_data['student_scores'] and course in previous_data['student_scores'][student_name]:
                            prev_score = previous_data['student_scores'][student_name][course]
                            score_change = round(score - prev_score, 1)
                        
                        top_performers.append({
                            "name": student_name,
                            "course": course,
                            "score": f"{score:.1f}",
                            "score_change": score_change,
                            "is_new": is_new
                        })
                except (ValueError, TypeError):
                    # Skip non-numeric values
                    continue
        
        # Sort top performers by score (descending)
        top_performers = sorted(top_performers, key=lambda x: float(x["score"]), reverse=True)
        
        # Track all student scores for future comparisons
        student_scores = {}
        for _, row in df.iterrows():
            student_name = row["student_name"]
            student_scores[student_name] = {}
            
            for course in course_columns:
                if course == "Precalculus":  # Skip problematic courses
                    continue
                # Skip if not enrolled
                if row[course] == "N/A" or pd.isna(row[course]) or row[course] == "":
                    continue
                
                try:
                    student_scores[student_name][course] = float(row[course])
                except (ValueError, TypeError):
                    continue
        
        # Prepare current data for caching
        current_data = {
            'timestamp': timestamp,
            'students': list(df["student_name"].unique()),
            'courses': current_courses,
            'student_scores': student_scores,
            'overall': {
                'average_score': average_score,
                'a_grade_percentage': a_grade_percentage
            }
        }
        
        # Prepare template context
        context = {
            'timestamp': timestamp,
            'current_year': current_year,
            'batch_id': batch_id,
            'students_processed': students_processed,
            'students_success_rate': students_success_rate,
            'courses': courses_sorted,
            'average_score': average_score,
            'average_score_change': average_score_change,
            'a_grade_percentage': a_grade_percentage,
            'a_grade_change': a_grade_change,
            'underperforming_students': underperforming_students,
            'at_risk_students': at_risk_students,
            'top_performers': top_performers
        }
        
        return current_data, context
        
    except Exception as e:
        logger.error(f"Error processing grades data: {e}")
        raise

def generate_report(grades_csv_path: str, template_path: str, output_path: str, cache_file: str) -> None:
    """
    Generate day-on-day performance report
    
    Args:
        grades_csv_path: Path to CSV file with grades data
        template_path: Path to template file
        output_path: Path to output file
        cache_file: Path to cache file for storing data
    """
    try:
        # Get logo path
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "emails", "logo.png")
        logo_base64 = get_image_base64(logo_path)
        
        # Load previous data for comparison
        previous_data = load_previous_data(cache_file)
        
        # Process grades data
        current_data, context = process_grades_data(grades_csv_path, previous_data)
        
        # Add logo to context
        context['logo_base64'] = logo_base64
        
        # Load template
        template_loader = jinja2.FileSystemLoader(os.path.dirname(template_path))
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template(os.path.basename(template_path))
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate HTML
        html_content = template.render(**context)
        
        # Write HTML to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        logger.info(f"Day-on-day report generated: {output_path}")
        
        # Save current data for future comparisons
        save_current_data(current_data, cache_file)
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Generate day-on-day performance report")
    parser.add_argument("--grades", required=True, help="Path to grades CSV file")
    parser.add_argument("--template", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "performance_day_on_day.html"), help="Path to template file")
    parser.add_argument("--output", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated", "performance_day_on_day.html"), help="Path to output file")
    parser.add_argument("--cache", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "grades_cache.json"), help="Path to cache file")
    
    args = parser.parse_args()
    
    try:
        # Generate report
        generate_report(args.grades, args.template, args.output, args.cache)
        print(f"Day-on-day report generated: {args.output}")
    except Exception as e:
        print(f"Error generating report: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main()) 