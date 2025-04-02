#!/usr/bin/env python3
"""
Test script for generating email reports
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from emails.report_generator import generate_email_html

def main():
    """Generate a test report from notion_grades.csv and open it in the browser"""
    # Define paths
    grades_csv_path = os.path.join(parent_dir, "notion_processor", "data", "notion_grades.csv")
    template_path = os.path.join(current_dir, "templates", "report_template.html")
    output_path = os.path.join(current_dir, "generated", "test_report.html")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Generating test report from {grades_csv_path}")
    print(f"Using template: {template_path}")
    print(f"Output will be saved to: {output_path}")
    
    # Generate the report
    generate_email_html(grades_csv_path, template_path, output_path)
    
    print(f"\nTest report successfully generated!")
    print(f"File saved to: {os.path.abspath(output_path)}")
    print("\nThis report includes these improvements:")
    print("1. Correctly counts only enrolled students per course")
    print("2. Excludes Precalculus data with explanatory footnote")
    print("3. Provides more accurate statistics by filtering N/A values")
    
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