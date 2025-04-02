#!/usr/bin/env python3
"""
Improved report generator for Canvas API data
Shows average scores instead of GPA and includes all underperforming students
"""

import os
import pandas as pd
import jinja2
from datetime import datetime
from typing import List, Dict, Any

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

def generate_email_html(grades_csv_path: str, template_path: str, output_path: str) -> None:
    """
    Generate HTML email report from grades data.
    
    Args:
        grades_csv_path: Path to the CSV file containing grades data
        template_path: Path to the HTML template file
        output_path: Path to save the generated HTML file
    """
    # Read grades data
    df = pd.read_csv(grades_csv_path)
    
    # Get timestamp
    timestamp = datetime.now().strftime("%B %d, %Y - %H:%M:%S")
    date = datetime.now().strftime("%B %d, %Y")
    
    # Get batch ID from the data
    batch_id = df["Update Batch"].iloc[0] if "Update Batch" in df.columns else "Unknown"
    
    # Count total students
    students_processed = len(df["student_name"].unique())
    
    # Get all course columns (exclude non-course columns)
    non_course_columns = [
        "student_name", "student_chinese_name", "student_english_name", 
        "Is Latest Batch", "Updated Time", "Update Batch"
    ]
    course_columns = [col for col in df.columns if col not in non_course_columns]
    
    # Exclude Precalculus from analysis as requested due to data issues
    if "Precalculus" in course_columns:
        course_columns.remove("Precalculus")
    
    course_count = len(course_columns)
    
    # Calculate course statistics
    courses_data = []
    for course in course_columns:
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
        
        courses_data.append({
            "name": course,
            "student_count": student_count,  # This is now actual enrollment count
            "avg_score": f"{avg_score:.1f}",
            "a_grade_percent": a_grade_percent,
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
            if row[course] == "N/A" or pd.isna(row[course]) or row[course] == "":
                continue
            try:
                score = float(row[course])
                all_scores.append(score)
            except (ValueError, TypeError):
                continue
    
    average_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
    
    # Find underperforming students (below 90%)
    underperforming_students = []
    
    for _, row in df.iterrows():
        student_name = row["student_name"]
        
        for course in course_columns:
            # Skip students not enrolled in this course
            if row[course] == "N/A" or pd.isna(row[course]) or row[course] == "":
                continue
                
            try:
                score = float(row[course])
                if score < 90:
                    needed_improvement = 90 - score
                    underperforming_students.append({
                        "name": student_name,
                        "course": course,
                        "score": f"{score:.1f}",
                        "grade_class": get_grade_class(score),
                        "needed_improvement": f"{needed_improvement:.1f}"
                    })
            except (ValueError, TypeError):
                # Skip non-numeric values
                continue
    
    # Sort underperforming students by score (ascending) - NO LIMIT applied
    underperforming_students = sorted(underperforming_students, key=lambda x: float(x["score"]))
    
    # Find at-risk students (90-92%)
    at_risk_students = []
    
    for _, row in df.iterrows():
        student_name = row["student_name"]
        
        for course in course_columns:
            # Skip students not enrolled in this course
            if row[course] == "N/A" or pd.isna(row[course]) or row[course] == "":
                continue
                
            try:
                score = float(row[course])
                if 90 <= score < 93:
                    at_risk_students.append({
                        "name": student_name,
                        "course": course,
                        "score": f"{score:.1f}"
                    })
            except (ValueError, TypeError):
                # Skip non-numeric values
                continue
    
    # Find top performers (above 100%)
    top_performers = []
    
    for _, row in df.iterrows():
        student_name = row["student_name"]
        
        for course in course_columns:
            # Skip students not enrolled in this course
            if row[course] == "N/A" or pd.isna(row[course]) or row[course] == "":
                continue
                
            try:
                score = float(row[course])
                if score > 100:
                    top_performers.append({
                        "name": student_name,
                        "course": course,
                        "score": f"{score:.1f}"
                    })
            except (ValueError, TypeError):
                # Skip non-numeric values
                continue
    
    # Sort top performers by score (descending) - NO LIMIT applied
    top_performers = sorted(top_performers, key=lambda x: float(x["score"]), reverse=True)
    
    # Identify priority students based on multiple failing courses or very low scores
    priority_students = []
    student_course_count = {}
    student_low_scores = {}
    
    for student in underperforming_students:
        name = student["name"]
        score = float(student["score"])
        
        if name not in student_course_count:
            student_course_count[name] = 0
            student_low_scores[name] = []
            
        student_course_count[name] += 1
        
        if score < 60:
            student_low_scores[name].append(f"{student['course']} ({score:.1f}%)")
    
    for name, count in student_course_count.items():
        if count >= 3:
            priority_students.append({
                "name": name,
                "reason": f"Underperforming in {count} courses"
            })
        elif student_low_scores.get(name, []):
            priority_students.append({
                "name": name,
                "reason": f"Very low scores in: {', '.join(student_low_scores[name])}"
            })
    
    # Calculate success rate (always 100% as we're only processing successful records)
    students_success_rate = 100
    
    # Prepare template context
    context = {
        "timestamp": timestamp,
        "date": date,
        "batch_id": batch_id,
        "students_processed": students_processed,
        "students_success_rate": students_success_rate,
        "course_count": course_count,
        "average_score": average_score,  # Using average score instead of GPA
        "a_grade_percentage": a_grade_percentage,
        "courses_sorted": courses_sorted,
        "underperforming_students": underperforming_students,
        "at_risk_students": at_risk_students,
        "top_performers": top_performers,
        "priority_students": priority_students
    }
    
    # Create a modified template with average score instead of GPA
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Replace GPA text with Average Score
    template_content = template_content.replace(
        '<div class="stat-label">Average GPA</div>', 
        '<div class="stat-label">Average Score</div>'
    )
    template_content = template_content.replace(
        '<div>Class of 2025</div>',
        '<div>Across All Courses</div>'
    )
    
    # Create Jinja2 template with the modified content
    template = jinja2.Template(template_content)
    
    # Generate HTML
    html_content = template.render(**context)
    
    # Add footnote about Precalculus
    precalculus_note = '''
    <div class="footer">
        <p><strong>Note:</strong> Precalculus has been excluded from this analysis due to data inconsistencies.</p>
        <p><strong>Note:</strong> All underperforming students are shown without limits to provide complete visibility.</p>
    </div>'''
    
    # Insert footnote before closing body tag
    html_content = html_content.replace('</body>', f'{precalculus_note}\n</body>')
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    print(f"Email HTML generated at: {output_path}")

if __name__ == "__main__":
    # Example usage if run directly
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python report_generator.py <grades_csv_path> <template_path> <output_path>")
        sys.exit(1)
        
    generate_email_html(sys.argv[1], sys.argv[2], sys.argv[3]) 