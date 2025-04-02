import smtplib
import os
import ssl
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv(dotenv_path="config/.env")

class EnhancedEmailNotifier:
    def __init__(self):
        # Load email configuration from environment variables
        self.sender_email = os.getenv("EMAIL_SENDER")
        self.sender_password = os.getenv("EMAIL_PASSWORD")
        self.recipient_email = os.getenv("EMAIL_RECIPIENT")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        
        # Define template paths
        self.success_template_path = os.path.join("emails", "templates", "success_template.html")
        self.failure_template_path = os.path.join("emails", "templates", "failure_template.html")
        
        # Check if email is configured
        self.is_configured = bool(self.sender_email and self.sender_password and self.recipient_email)
        
    def _read_template(self, template_path):
        """Read an HTML template from file"""
        try:
            with open(template_path, 'r') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading template {template_path}: {str(e)}")
            return ""
            
    def _replace_placeholders(self, template, replacements):
        """Replace placeholders in template with actual values"""
        for key, value in replacements.items():
            placeholder = f"{{{{{key}}}}}"
            template = template.replace(placeholder, str(value))
        return template
    
    def _gather_course_statistics(self):
        """Gather statistics about courses from grades.csv"""
        try:
            grades_path = os.path.join("data", "grades.csv")
            if not os.path.exists(grades_path):
                return "No course data available"
                
            df = pd.read_csv(grades_path)
            
            # Group by course and calculate stats
            course_stats = df.groupby(['course_name', 'course_chinese_name']).agg({
                'student_name': 'count',
                'score': ['mean', 'min', 'max']
            }).reset_index()
            
            # Format the results as HTML table rows
            html_rows = ""
            for _, row in course_stats.iterrows():
                course_name = f"{row['course_chinese_name']} ({row['course_name']})"
                students = row[('student_name', 'count')]
                avg_score = f"{row[('score', 'mean')]:.2f}"
                
                html_rows += f"""
                <tr>
                    <td>{course_name}</td>
                    <td>{students}</td>
                    <td>{avg_score}</td>
                </tr>
                """
            
            return html_rows
            
        except Exception as e:
            print(f"Error gathering course statistics: {str(e)}")
            return "<tr><td colspan='3'>Error gathering course statistics</td></tr>"
    
    def send_notification(self, subject, html_content):
        """Send an email notification with the provided subject and HTML content."""
        if not self.is_configured:
            print("Email notification not configured. Skipping notification.")
            return False
        
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = self.recipient_email
            message["Subject"] = subject
            
            # Attach HTML content
            message.attach(MIMEText(html_content, "html"))
            
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
            
    def send_success_notification(self, students_processed, records_added, batch_id="N/A", execution_time="N/A"):
        """Send a success notification with summary of the run."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Get course statistics
        course_stats = self._gather_course_statistics()
        
        # Read the template
        template = self._read_template(self.success_template_path)
        
        # Replace placeholders
        replacements = {
            "timestamp": timestamp,
            "students_processed": students_processed,
            "records_added": records_added,
            "execution_time": execution_time,
            "batch_id": batch_id,
            "course_stats": course_stats,
            "date": date
        }
        html_content = self._replace_placeholders(template, replacements)
        
        # Send the email
        subject = f"✅ Canvas Grades Collection Success - {timestamp}"
        return self.send_notification(subject, html_content)
        
    def send_failure_notification(self, error_message):
        """Send a failure notification with error details."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Read the template
        template = self._read_template(self.failure_template_path)
        
        # Replace placeholders
        replacements = {
            "timestamp": timestamp,
            "error_message": error_message,
            "date": date
        }
        html_content = self._replace_placeholders(template, replacements)
        
        # Send the email
        subject = f"❌ Canvas Grades Collection Failed - {timestamp}"
        return self.send_notification(subject, html_content) 