#!/usr/bin/env python3
"""
Test script for the improved report generator
Shows average scores instead of GPA and includes all underperforming students
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import our improved generator
from emails.testing.improved_report_generator import generate_email_html

def main():
    """Generate a test report with average scores and no student limits"""
    # Define paths
    grades_csv_path = os.path.join(parent_dir, "notion_processor", "data", "notion_grades.csv")
    template_path = os.path.join(parent_dir, "emails", "templates", "report_template.html")
    output_path = os.path.join(current_dir, "improved_report.html")
    
    print(f"Generating improved test report from {grades_csv_path}")
    print(f"Using template: {template_path}")
    print(f"Output will be saved to: {output_path}")
    
    # Generate the report with our improved generator
    generate_email_html(grades_csv_path, template_path, output_path)
    
    print(f"\nImproved test report successfully generated!")
    print(f"File saved to: {os.path.abspath(output_path)}")
    print(f"\nNew improvements:")
    print("1. Uses average scores instead of GPA")
    print("2. Shows ALL underperforming students without limits")
    print("3. Shows ALL top performers without limits")
    
    # Attempt to open the report in the browser automatically (macOS only)
    try:
        import subprocess
        subprocess.call(['open', output_path])
        print("\nThe report should open automatically in your browser.")
    except Exception as e:
        print(f"\nCould not open the report automatically: {e}")
        print("Please open it manually.")

if __name__ == "__main__":
    main() 