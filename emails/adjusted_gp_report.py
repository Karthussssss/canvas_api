#!/usr/bin/env python3
"""
Script to generate an adjusted HTML report for General Psychology with 17 points added
"""

import os
import sys
import pandas as pd
from pathlib import Path
import argparse

# Add the parent directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the report generator
from emails.report_generator import generate_email_html
from emails.notifier.enhanced_email_notifier import EnhancedEmailNotifier

def send_report_email(report_path):
    """Send the adjusted report via email"""
    print("Sending adjusted General Psychology report via email...")
    
    if not os.path.exists(report_path):
        print(f"Error: Report not found at {report_path}")
        return False
    
    # Read the HTML content
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"Error reading report: {str(e)}")
        return False
    
    # Create email notifier
    notifier = EnhancedEmailNotifier()
    
    if not notifier.is_configured:
        print("\nEmail settings not configured. Please set the following environment variables in config/.env:")
        print("  - EMAIL_SENDER: Your email address")
        print("  - EMAIL_PASSWORD: Your email password or app password")
        print("  - EMAIL_RECIPIENT: Recipient email address(es), comma-separated")
        print("  - EMAIL_CC: Optional CC recipient email address(es), comma-separated")
        return False
    
    # Send the email with the report
    subject = "📊 General Psychology Adjusted Grades Report (+17 points)"
    success = notifier.send_notification(subject, html_content)
    
    if success:
        recipient_str = ", ".join(notifier.recipient_emails)
        cc_str = ", ".join(notifier.cc_emails) if notifier.cc_emails else "None"
        print(f"\nAdjusted report successfully sent to:")
        print(f"- Recipients: {recipient_str}")
        print(f"- CC: {cc_str}")
        return True
    else:
        print("\nFailed to send adjusted report. Check the error message above.")
        return False

def main():
    """Generate an HTML report with General Psychology scores adjusted by +17 points"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Generate an adjusted report for General Psychology with +17 points')
    parser.add_argument('--send-email', action='store_true', help='Send the report via email after generation')
    args = parser.parse_args()
    
    # Define file paths
    original_grades_csv_path = os.path.join(parent_dir, "notion_processor", "data", "notion_grades.csv")
    adjusted_grades_csv_path = os.path.join(parent_dir, "notion_processor", "data", "notion_grades_adjusted_gp.csv")
    template_path = os.path.join(current_dir, "templates", "report_template.html")
    output_path = os.path.join(current_dir, "generated", "gp_adjusted_report.html")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Reading original grades data from {original_grades_csv_path}")
    
    # Read the original data
    df = pd.read_csv(original_grades_csv_path)
    
    # Create a copy for the adjusted data
    adjusted_df = df.copy()
    
    # Add the adjusted General Psychology course
    if "General Psychology" in df.columns:
        print("Adding 'General Psychology - Adjusted' with +17 points")
        
        # Create a new column with the adjusted scores
        adjusted_df["General Psychology - Adjusted"] = df["General Psychology"].apply(
            lambda x: float(x) + 17 if x != "N/A" and pd.notna(x) and x != "" else x
        )
        
        # Count how many students will get an A with the adjustment
        a_grade_count = 0
        total_students = 0
        
        for idx, row in df.iterrows():
            if row["General Psychology"] != "N/A" and pd.notna(row["General Psychology"]) and row["General Psychology"] != "":
                total_students += 1
                original_score = float(row["General Psychology"])
                if original_score >= 73:  # Students with 73+ will get an A after +17 points
                    a_grade_count += 1
        
        a_grade_percentage = (a_grade_count / total_students * 100) if total_students > 0 else 0
        
        print(f"\nWith original threshold of 90 for an A grade:")
        print(f"- {a_grade_count} out of {total_students} students ({a_grade_percentage:.1f}%) will get an A in General Psychology after +17 adjustment")
        print(f"- Students with original scores of 73 or higher will get an A (73 + 17 = 90)")
        
        # Save the adjusted data
        adjusted_df.to_csv(adjusted_grades_csv_path, index=False)
        print(f"Adjusted data saved to {adjusted_grades_csv_path}")
    else:
        print("Warning: 'General Psychology' column not found in the data")
        return
    
    print(f"Using template: {template_path}")
    print(f"Output will be saved to: {output_path}")
    
    # Generate the HTML report with the adjusted data
    generate_email_html(adjusted_grades_csv_path, template_path, output_path)
    
    print(f"\nAdjusted report successfully generated!")
    print(f"File saved to: {os.path.abspath(output_path)}")
    print("\nThis report includes an adjusted analysis for General Psychology:")
    print("- Added 'General Psychology - Adjusted' column with +17 points for each student")
    print("- Students with original scores of 73+ will get an A grade (after +17 adjustment)")
    
    # Attempt to open the report in the browser automatically (macOS only)
    try:
        import subprocess
        subprocess.call(['open', output_path])
        print("\nThe report should open automatically in your browser.")
    except Exception as e:
        print(f"\nCould not open the report automatically: {e}")
        print("Please open it manually.")
    
    # Send email if requested
    if args.send_email:
        send_report_email(output_path)

if __name__ == "__main__":
    main() 