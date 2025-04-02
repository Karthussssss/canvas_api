#!/usr/bin/env python3
"""
Enhanced Email Notifier for Canvas API
Sends beautifully formatted HTML emails with grade reports
"""

import smtplib
import os
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import datetime
import sys
from pathlib import Path

# Add parent directory to path to import from emails
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now import from parent project
from emails.report_generator import generate_email_html

# Load environment variables
load_dotenv()

class EnhancedEmailNotifier:
    def __init__(self):
        # Load email configuration from environment variables
        self.sender_email = os.getenv("EMAIL_SENDER")
        self.sender_password = os.getenv("EMAIL_PASSWORD")
        self.recipient_email = os.getenv("EMAIL_RECIPIENT")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        
        # Check if email is configured
        self.is_configured = bool(self.sender_email and self.sender_password and self.recipient_email)
        
    def send_notification(self, subject, message_body, is_success=True):
        """Send an email notification with the provided subject and message."""
        if not self.is_configured:
            print("Email notification not configured. Skipping notification.")
            return False
        
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = self.recipient_email
            
            # Add current timestamp to subject
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message["Subject"] = subject
            
            # Attach HTML content
            message.attach(MIMEText(message_body, "html"))
            
            # Create a secure SSL context
            context = ssl.create_default_context()
            
            # Connect to server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
                
            print(f"Email notification sent to {self.recipient_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
            
    def send_enhanced_report(self, students_processed, records_added):
        """Send an enhanced HTML report with detailed grade analysis."""
        try:
            # Define file paths
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            grades_csv_path = os.path.join(current_dir, "..", "notion_processor", "data", "notion_grades.csv")
            template_path = os.path.join(current_dir, "templates", "report_template.html")
            output_path = os.path.join(current_dir, "generated", "grades_report.html")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Generate the HTML report
            html_content = generate_email_html(grades_csv_path, template_path, output_path)
            
            # Get the date for the subject line
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # Send the email
            subject = f"📊 Canvas Grades Report: Performance Summary & Alerts [{today}]"
            return self.send_notification(subject, html_content, is_success=True)
            
        except Exception as e:
            print(f"Error generating enhanced report: {str(e)}")
            # Fall back to simple success notification
            return self.send_simple_success_notification(students_processed, records_added)
    
    def send_simple_success_notification(self, students_processed, records_added):
        """Send a simple success notification with summary of the run."""
        subject = "Canvas Grades Collection Success"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create a simpler HTML message
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto;">
            <div style="background-color: #4CAF50; color: white; padding: 20px; text-align: center;">
                <h1>✅ Canvas Grades Collection Success</h1>
                <p>Run Time: {timestamp}</p>
            </div>
            <div style="padding: 20px;">
                <h2>Canvas API Academic Data Collector completed successfully!</h2>
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Summary:</h3>
                    <ul>
                        <li><strong>Students processed:</strong> {students_processed}</li>
                        <li><strong>Records added to Notion:</strong> {records_added}</li>
                        <li><strong>Full logs available in:</strong> logs/canvas_api.log</li>
                    </ul>
                </div>
                <p>For more detailed analysis, please check the enhanced report feature.</p>
            </div>
            <div style="background-color: #f1f1f1; padding: 10px; text-align: center; font-size: 0.8em; color: #666;">
                <p>This is an automated message from the Canvas API Academic Data Collector.</p>
                <p>Version 1.0 | {timestamp.split()[0]}</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_notification(subject, html_message, is_success=True)
        
    def send_failure_notification(self, error_message):
        """Send a failure notification with error details."""
        subject = "Canvas Grades Collection Failed"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto;">
            <div style="background-color: #f44336; color: white; padding: 20px; text-align: center;">
                <h1>❌ Canvas Grades Collection Failed</h1>
                <p>Run Time: {timestamp}</p>
            </div>
            <div style="padding: 20px;">
                <h2>Canvas API Academic Data Collector encountered an error</h2>
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0; font-family: monospace; white-space: pre-wrap;">
{error_message}
                </div>
                <p>Please check the logs for more information: <code>logs/canvas_api.log</code></p>
            </div>
            <div style="background-color: #f1f1f1; padding: 10px; text-align: center; font-size: 0.8em; color: #666;">
                <p>This is an automated message from the Canvas API Academic Data Collector.</p>
                <p>Version 1.0 | {timestamp.split()[0]}</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_notification(subject, html_message, is_success=False) 