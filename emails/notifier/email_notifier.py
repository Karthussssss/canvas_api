#!/usr/bin/env python3
import smtplib
import os
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import datetime
import sys

# Add the parent directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the enhanced email notifier
from emails.notifier.enhanced_email_notifier import EnhancedEmailNotifier

# Load environment variables from config/.env
env_path = os.path.join(parent_dir, "config", ".env")
load_dotenv(env_path)

class EmailNotifier:
    def __init__(self):
        # Load email configuration from environment variables
        self.sender_email = os.getenv("EMAIL_SENDER")
        self.sender_password = os.getenv("EMAIL_PASSWORD")
        
        # Support for multiple recipients (comma-separated email addresses)
        self.recipient_emails = [email.strip() for email in os.getenv("EMAIL_RECIPIENT", "").split(",") if email.strip()]
        
        # Support for CC recipients (comma-separated email addresses)
        self.cc_emails = [email.strip() for email in os.getenv("EMAIL_CC", "").split(",") if email.strip()]
        
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        
        # Check if email is configured
        self.is_configured = bool(self.sender_email and self.sender_password and self.recipient_emails)
        
        # Create an instance of the enhanced email notifier
        self.enhanced_notifier = EnhancedEmailNotifier()
        
    def send_notification(self, subject, message_body, is_success=True):
        """Send an email notification with the provided subject and message."""
        if not self.is_configured:
            print("Email notification not configured. Skipping notification.")
            return False
        
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = ", ".join(self.recipient_emails)
            
            # Add CC recipients if available
            if self.cc_emails:
                message["Cc"] = ", ".join(self.cc_emails)
            
            # Add current timestamp to subject
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message["Subject"] = f"{subject} - {timestamp}"
            
            # Add status icon to message body
            status_icon = "✅" if is_success else "❌"
            html_message = f"""
            <html>
            <body>
                <h2>{status_icon} {subject}</h2>
                <p>Run Time: {timestamp}</p>
                <hr>
                <pre>{message_body}</pre>
                <hr>
                <p>This is an automated message from the Canvas API Academic Data Collector.</p>
                <p>Powered by Beecoming Inc.</p>
            </body>
            </html>
            """
            
            # Attach HTML content
            message.attach(MIMEText(html_message, "html"))
            
            # Create a secure SSL context
            context = ssl.create_default_context()
            
            # Get all recipients for sending
            all_recipients = self.recipient_emails.copy()
            if self.cc_emails:
                all_recipients.extend(self.cc_emails)
            
            # Connect to server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
                
            recipient_str = ", ".join(self.recipient_emails)
            cc_str = ", ".join(self.cc_emails) if self.cc_emails else "None"
            print(f"Email notification sent to recipients: {recipient_str}, CC: {cc_str}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
            
    def send_success_notification(self, students_processed, records_added):
        """Send a success notification with summary of the run and enhanced report."""
        try:
            # Try to send the enhanced report using our improved report generator
            return self.enhanced_notifier.send_enhanced_report(students_processed, records_added)
        except Exception as e:
            print(f"Error sending enhanced report: {str(e)}. Falling back to simple notification.")
            
            # Fall back to the simple notification if enhanced report fails
            subject = "Canvas Grades Collection Success"
            message = f"""
Canvas API Academic Data Collector completed successfully!

Summary:
- Students processed: {students_processed}
- Records added to Notion: {records_added}
- Full logs available in: canvas_api.log
            """
            return self.send_notification(subject, message, is_success=True)
        
    def send_failure_notification(self, error_message):
        """Send a failure notification with error details."""
        try:
            # Try to send the enhanced failure notification
            return self.enhanced_notifier.send_failure_notification(error_message)
        except Exception as e:
            print(f"Error sending enhanced failure notification: {str(e)}. Falling back to simple notification.")
            
            # Fall back to the simple notification if enhanced notification fails
            subject = "Canvas Grades Collection Failed"
            message = f"""
Canvas API Academic Data Collector encountered an error:

Error details:
{error_message}

Please check the logs for more information: canvas_api.log
            """
            return self.send_notification(subject, message, is_success=False) 