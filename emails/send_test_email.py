#!/usr/bin/env python3
"""
Send test report email
This script sends the generated test report to the configured recipient
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from emails.notifier.enhanced_email_notifier import EnhancedEmailNotifier
import datetime
from email.mime.text import MIMEText

def send_test_report():
    """Send the test report via email"""
    print("Sending test report email...")
    
    # Get the test report file path
    report_path = os.path.join(current_dir, "generated", "test_report.html")
    
    if not os.path.exists(report_path):
        print(f"Error: Test report not found at {report_path}")
        print("Please run python emails/test_report.py first to generate the report.")
        return False
    
    # Read the HTML content
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"Error reading test report: {str(e)}")
        return False
    
    # Create email notifier
    notifier = EnhancedEmailNotifier()
    
    if not notifier.is_configured:
        print("\nEmail settings not configured. Please set the following environment variables:")
        print("  - EMAIL_SENDER: Your email address")
        print("  - EMAIL_PASSWORD: Your email password or app password")
        print("  - EMAIL_RECIPIENT: Recipient email address")
        print("  - SMTP_SERVER: SMTP server (default: smtp.gmail.com)")
        print("  - SMTP_PORT: SMTP port (default: 587)")
        print("\nThese should be set in the config/.env file")
        return False
    
    # Get the date for the subject line
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Send the email with the test report
    subject = f"📊 Test Canvas Grades Report [{today}]"
    success = notifier.send_notification(subject, html_content)
    
    if success:
        print(f"\nTest report successfully sent to {notifier.recipient_email}")
        return True
    else:
        print("\nFailed to send test report. Check the error message above.")
        return False

if __name__ == "__main__":
    send_test_report() 