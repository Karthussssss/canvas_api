#!/usr/bin/env python3
"""
Report generator for Canvas API data
Transforms grade data into HTML email reports
"""

import os
import pandas as pd
import jinja2
from datetime import datetime
from typing import List, Dict, Any
import re
import base64
from pathlib import Path
import numpy as np

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
        print(f"Warning: Could not embed image {image_path}: {e}")
        return ""

def remove_emojis(text: str) -> str:
    """Remove emojis from text to prevent encoding issues"""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"
        "]+", 
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)

def generate_email_html(grades_csv_path: str, template_path: str, output_path: str) -> None:
    """
    Generate HTML email report from grades data.
    
    Args:
        grades_csv_path: Path to the CSV file containing grades data
        template_path: Path to the HTML template file
        output_path: Path to save the generated HTML file
    """
    # Get logo path - using relative path based on current file location
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "logo.png")
    logo_base64 = get_image_base64(logo_path)
    
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
        
        # Create link for course name if available
        course_name = course
        if course in COURSE_NOTION_LINKS:
            course_name = f'<a href="{COURSE_NOTION_LINKS[course]}" target="_blank" style="color: #2196F3; text-decoration: none;">{course}</a>'
        
        courses_data.append({
            "name": course_name,
            "raw_name": course,  # Keep the raw name for sorting
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
    
    # Sort underperforming students by score (ascending) - show all without limit
    underperforming_students = sorted(underperforming_students, key=lambda x: float(x["score"]))
    
    # Find at-risk students (90-92.5%)
    at_risk_students = []
    
    for _, row in df.iterrows():
        student_name = row["student_name"]
        
        for course in course_columns:
            # Skip students not enrolled in this course
            if row[course] == "N/A" or pd.isna(row[course]) or row[course] == "":
                continue
                
            try:
                score = float(row[course])
                if 90 <= score < 92.5:
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
    
    # Sort top performers by score (descending) - show all without limit
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
    
    # Sort priority students by the number of courses they're struggling with
    # This ensures the most critical cases appear at the top
    priority_students = sorted(priority_students, 
                             key=lambda x: x["reason"].count("courses") if "courses" in x["reason"] else 0, 
                             reverse=True)
    
    # No limit applied to priority_students to ensure all critical cases are reported
    
    # Calculate success rate (always 100% as we're only processing successful records)
    students_success_rate = 100
    
    # Format course enrollment information
    course_enrollment_html = ""
    # Fix sorting error by using raw course names without attempting to use COURSE_NOTION_LINKS for sorting
    ordered_courses = sorted(course_columns)
    
    for course_col in ordered_courses:
        course_name = course_col.replace('Score: ', '')
        count = len(df[df[course_col] != "N/A"])
        avg_score = df[course_col][df[course_col] != "N/A"].mean() if course_col in df.columns else "N/A"
        
        # Check if we have a Notion link for this course
        course_display = course_name
        if course_name in COURSE_NOTION_LINKS:
            course_display = f'<a href="{COURSE_NOTION_LINKS[course_name]}" target="_blank" style="color: #2196F3; text-decoration: none; font-weight: bold;">{course_name}</a>'
        
        # Format average score properly
        formatted_avg = f"{avg_score:.1f}" if isinstance(avg_score, (int, float)) else "N/A"
        
        # Format with the average score and hyperlink if available
        course_enrollment_html += f"""
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">{course_display}</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{count}</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{formatted_avg}</td>
        </tr>
        """
    
    # Prepare template context
    context = {
        "timestamp": timestamp,
        "date": date,
        "batch_id": batch_id,
        "students_processed": students_processed,
        "students_success_rate": students_success_rate,
        "course_count": course_count,
        "a_grade_percentage": a_grade_percentage,
        "average_gpa": average_score,  # We're using average score instead of GPA
        "courses_sorted": courses_sorted,
        "underperforming_students": underperforming_students,
        "at_risk_students": at_risk_students,
        "top_performers": top_performers,
        "priority_students": priority_students,
        "logo_base64": logo_base64,  # Add the base64 encoded logo
        "course_enrollment_html": course_enrollment_html
    }
    
    # Create a modified template with average score instead of GPA
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Add UTF-8 meta tag to ensure proper Chinese character rendering
    if "<head>" in template_content and "<meta charset=" not in template_content:
        template_content = template_content.replace(
            "<head>",
            '<head>\n    <meta charset="UTF-8">'
        )
    
    # Add CSS to fix small percentage display in progress bars
    if "</style>" in template_content:
        fix_small_percentage_css = """
        .progress-bar {
            min-width: 30px; /* Ensure minimum width for small percentages */
            position: relative; /* For positioning the text */
        }
        .progress-bar::after {
            content: attr(data-percent);
            position: absolute;
            left: 0;
            right: 0;
            text-align: center;
            color: white;
        }
        """
        template_content = template_content.replace(
            "</style>",
            f"{fix_small_percentage_css}\n    </style>"
        )
    
    # Fix percentage display in progress bars - use data attribute for percentage
    template_content = template_content.replace(
        '<div class="progress-bar" style="width: {{ course.a_grade_percent }}%; background-color: {{ course.color }};">{{ course.a_grade_percent }}</div>',
        '<div class="progress-bar" style="width: {{ course.a_grade_percent }}%; background-color: {{ course.color }};" data-percent="{{ course.a_grade_percent }}%"></div>'
    )
    
    # Replace GPA text with Average Score
    template_content = template_content.replace(
        '<div class="stat-label">Average GPA</div>', 
        '<div class="stat-label">Average Score</div>'
    )
    template_content = template_content.replace(
        '<div>Class of 2025</div>',
        '<div>Across All Courses</div>'
    )
    
    # Remove all emoji characters from template to prevent encoding issues
    template_content = template_content.replace("✅", "")  # Remove checkmark
    template_content = template_content.replace("📈", "")  # Remove chart
    template_content = template_content.replace("⚠️", "")  # Remove warning
    template_content = template_content.replace("🚨", "")  # Remove alert
    template_content = template_content.replace("🌟", "")  # Remove star
    template_content = template_content.replace("🏆", "")  # Remove trophy
    template_content = template_content.replace("🚩", "")  # Remove flag
    
    # Use text labels instead of emojis
    template_content = template_content.replace(
        "<h1>✅ Canvas Grades Collection Success</h1>",
        "<h1>Canvas Grades Collection Success</h1>"
    )
    template_content = template_content.replace(
        "<h2>📈 Course Performance Summary</h2>",
        "<h2>Course Performance Summary</h2>"
    )
    template_content = template_content.replace(
        "<h2>⚠️ Performance Concerns</h2>",
        "<h2>Performance Concerns</h2>"
    )
    template_content = template_content.replace(
        "<h2>🚨 At-Risk Students</h2>",
        "<h2>At-Risk Students</h2>"
    )
    template_content = template_content.replace(
        "<h2>🌟 Top Performers</h2>",
        "<h2>Top Performers</h2>"
    )
    template_content = template_content.replace(
        "<h2>🏆 Top Performers</h2>",
        "<h2>Top Performers</h2>"
    )
    template_content = template_content.replace(
        "<h2>🚩 Students Needing Immediate Outreach</h2>",
        "<h2>Students Needing Immediate Outreach</h2>"
    )
    
    # Update the description of at-risk students to match the actual filtering criteria
    template_content = template_content.replace(
        "<p>Students at risk of dropping from A to B (scores between 90-92%):</p>",
        "<p>Students at risk of dropping from A to B (scores between 90-92.5%):</p>"
    )
    
    # Attempt to catch any other problematic characters
    for i in range(0x1F300, 0x1F6FF):
        template_content = template_content.replace(chr(i), '')
    
    # Add logo to header
    logo_header = f'''
    <div style="text-align: center; margin-bottom: 20px;">
        <img src="{logo_base64}" alt="Beecoming Logo" style="max-width: 150px; height: auto;">
    </div>
    '''
    
    # Insert logo at the beginning of the content div
    template_content = template_content.replace(
        '<div class="content">',
        f'<div class="content">{logo_header}'
    )
    
    # Create Jinja2 template with the modified content
    template = jinja2.Template(template_content)
    
    # Generate HTML
    html_content = template.render(**context)
    
    # Add logo footer (smaller, at the bottom)
    logo_footer = f"""
    <div style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
        <img src="data:image/png;base64,{logo_base64}" alt="Beecoming Logo" style="width: 150px; height: auto; margin-bottom: 10px;">
        <p>Powered by Beecoming Inc.</p>
    </div>
    """
    
    # Create privacy statement in English and Chinese
    # Using separate variable for copyright year to avoid encoding issues
    privacy_statement = f'''
    <div style="margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px; font-size: 12px; color: #666;">
        <h3 style="margin-bottom: 10px; color: #444;">Privacy Statement</h3>
        <p>This report contains sensitive student academic data and is intended solely for authorized educational personnel. 
        The information in this report is confidential and must not be shared, distributed, or disclosed to unauthorized 
        individuals. Unauthorized disclosure may violate student privacy regulations and institutional policies.</p>
        
        <h3 style="margin: 15px 0 10px 0; color: #444;">隐私声明</h3>
        <p>本报告包含敏感的学生学术数据，仅供授权教育人员使用。
        报告中的信息为机密信息，不得与未经授权的个人共享、分发或披露。
        未经授权的披露可能违反学生隐私法规和机构政策。</p>
        
        <p style="margin-top: 20px; text-align: center;">Developed by Karthus | © {current_year} Beecoming Inc.</p>
    </div>
    '''
    
    # Add logo to footer with Precalculus note and privacy statement
    footer_with_logo = f'''
    <div class="footer">
        <p><strong>Note:</strong> Precalculus has been excluded from this analysis due to data inconsistencies.</p>
        <div style="text-align: center; margin-top: 20px;">
            <img src="{logo_base64}" alt="Beecoming Logo" style="max-width: 150px; height: auto;">
            <p>Powered by Beecoming Inc.</p>
        </div>
        {privacy_statement}
    </div>
    '''
    
    # Insert logo footer before closing body tag
    html_content = html_content.replace('</body>', f'{footer_with_logo}\n</body>')
    
    # Ensure HTML doctype declaration includes proper charset
    if "<!DOCTYPE html>" in html_content and "<meta charset=" not in html_content:
        html_content = html_content.replace(
            "<!DOCTYPE html>",
            '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        )
    
    # Write to file with explicit UTF-8 encoding
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Email HTML generated at: {output_path}")

if __name__ == "__main__":
    # Example usage if run directly
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python report_generator.py <grades_csv_path> <template_path> <output_path>")
        sys.exit(1)
        
    generate_email_html(sys.argv[1], sys.argv[2], sys.argv[3]) 