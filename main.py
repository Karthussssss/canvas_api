from utils.credential_manager import CredentialManager
from data_collectors.grades import GradesCollector
from utils.csv_handler import CSVHandler
from notion_processor.notion_main import main as process_notion
from emails.notifier.email_notifier import EmailNotifier
import sys
import os
import requests
import json

# Add the config directory to the path
config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
if config_dir not in sys.path:
    sys.path.insert(0, config_dir)

# Now import from config
from config import GRADES_CSV_PATH, STUDENT_TO_CHINESE_NAME, STUDENT_TO_PREFERRED_ENGLISH_NAME

# Add the notion_processor directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "notion_processor"))

import logging
from datetime import datetime
from notion_processor.utils.batch_manager import initialize_batch

# Configure logging
logging.basicConfig(
    filename='logs/canvas_api.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

NOTION_TOKEN = "ntn_j9650042443oA4qz4hiuMkA9Wb8hIlT77BASn5E7Kzyezv"
DATABASE_ID = "1cf23f2ff64b8072bba9cdb79ed3972a"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",  # Fixed space after Bearer
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_pages():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {"page_size": 100}  # Fixed parameter name
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for bad status codes
        data = response.json()
        print(json.dumps(data, indent=2))
        return data.get("results", [])
    except requests.exceptions.RequestException as e:
        print(f"Error making request to Notion API: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return []

def process_pages():
    pages = get_pages()
    for page in pages:
        try:
            page_id = page["id"]
            props = page["properties"]
            # Fixed property access - assuming "Course" is the correct property name
            course = props.get("Course", {}).get("title", [{}])[0].get("text", {}).get("content", "No course name")
            print(f"Page ID: {page_id}, Course: {course}")
        except (KeyError, IndexError) as e:
            print(f"Error processing page: {e}")

def collect_grades():
    """Collect grades for all students"""
    print("\n--- Starting grades collection ---\n")
    logging.info("Starting grades collection")
    
    # Initialize credential manager
    manager = CredentialManager()
    
    # Initialize CSV handler
    csv_handler = CSVHandler(GRADES_CSV_PATH)
    
    # Get all student names
    student_names = manager.get_all_student_names()
    
    if not student_names:
        print("No students found in credentials file.")
        logging.warning("No students found in credentials file.")
        return
    
    print(f"Found {len(student_names)} students in credentials file.")
    logging.info(f"Found {len(student_names)} students in credentials file.")
    
    # Process each student
    for student_name in student_names:
        print(f"\n=== Processing student: {student_name} ===\n")
        logging.info(f"Processing student: {student_name}")
        
        # Get student credentials
        credentials = manager.get_student_credentials(student_name)
        if not credentials:
            print(f"❌ No credentials found for {student_name}")
            logging.warning(f"No credentials found for {student_name}")
            continue
            
        # Make sure user_id is an integer
        user_id = credentials.get("user_id")
        if not user_id:
            print(f"❌ No user_id found for {student_name}")
            logging.warning(f"No user_id found for {student_name}")
            continue
            
        try:
            user_id = int(user_id)
        except ValueError:
            print(f"❌ Invalid user_id for {student_name}: {user_id}")
            logging.error(f"Invalid user_id for {student_name}: {user_id}")
            continue
            
        # Create grades collector
        collector = GradesCollector(
            student_name=student_name,
            api_key=credentials["api_key"],
            domain=credentials["domain"],
            user_id=user_id
        )
        
        try:
            # Collect grades data
            grades_data = collector.collect()
            
            # Save to CSV
            if grades_data:
                csv_handler.save_grades(grades_data)
                print(f"\n✅ Successfully collected grades for {student_name}")
                logging.info(f"Successfully collected grades for {student_name}")
            else:
                print(f"\n⚠️ No grades data collected for {student_name}")
                logging.warning(f"No grades data collected for {student_name}")
                
        except Exception as e:
            print(f"❌ Error processing {student_name}: {str(e)}")
            logging.error(f"Error processing {student_name}: {str(e)}")
    
    # After all students are processed, generate the Notion-friendly CSV
    print("\n--- Generating Notion-friendly grades format ---")
    logging.info("Generating Notion-friendly grades format")
    process_notion()
    
    print("\n--- Grades collection completed ---")
    logging.info("Grades collection completed")

def debug_student_mappings():
    """Print student name mappings for debugging"""
    print("\n--- Debugging Student Name Mappings ---")
    for student_name in STUDENT_TO_CHINESE_NAME.keys():
        chinese_name = STUDENT_TO_CHINESE_NAME.get(student_name, "")
        english_name = STUDENT_TO_PREFERRED_ENGLISH_NAME.get(student_name, "")
        print(f"Canvas name: {student_name} -> Chinese: {chinese_name}, English: {english_name}")
    print("--- End of Student Name Mappings ---\n")

def main():
    """Main entry point for Canvas API client."""
    
    start_time = datetime.now()
    print(f"\n--- Starting grades collection at {start_time} ---")
    logging.info(f"Starting grades collection at {start_time}")
    
    # Debug student name mappings
    debug_student_mappings()
    
    # Initialize email notifier
    email_notifier = EmailNotifier()
    
    students_processed = 0
    records_added = 0
    
    try:
        # Initialize update batch ID for this run
        batch_id = initialize_batch()
        print(f"Update Batch ID: {batch_id}")
        logging.info(f"Update Batch ID: {batch_id}")
        
        # Create credential manager
        manager = CredentialManager()
        
        # Initialize CSV handler
        csv_handler = CSVHandler(GRADES_CSV_PATH)
        
        # Get all student names
        student_names = manager.get_all_student_names()
        
        if not student_names:
            print("No students found in credentials file.")
            logging.warning("No students found in credentials file.")
            email_notifier.send_failure_notification("No students found in credentials file.")
            return
        
        print(f"\nFound {len(student_names)} students in credentials file.\n")
        logging.info(f"Found {len(student_names)} students in credentials file.")
        
        # Process each student
        for student_name in student_names:
            print(f"\n=== Processing student: {student_name} ===\n")
            logging.info(f"Processing student: {student_name}")
            
            # Get student credentials
            credentials = manager.get_student_credentials(student_name)
            if not credentials:
                print(f"❌ No credentials found for {student_name}")
                logging.warning(f"No credentials found for {student_name}")
                continue
                
            # Make sure user_id is an integer
            user_id = credentials.get("user_id")
            if not user_id:
                print(f"❌ No user_id found for {student_name}")
                logging.warning(f"No user_id found for {student_name}")
                continue
                
            try:
                user_id = int(user_id)
            except ValueError:
                print(f"❌ Invalid user_id for {student_name}: {user_id}")
                logging.error(f"Invalid user_id for {student_name}: {user_id}")
                continue
                
            # Create grades collector
            collector = GradesCollector(
                student_name=student_name,
                api_key=credentials["api_key"],
                domain=credentials["domain"],
                user_id=user_id
            )
            
            try:
                # Collect grades data
                grades_data = collector.collect()
                
                # Save to CSV
                if grades_data:
                    csv_handler.save_grades(grades_data)
                    print(f"\n✅ Successfully collected grades for {student_name}")
                    logging.info(f"Successfully collected grades for {student_name}")
                    students_processed += 1
                else:
                    print(f"\n⚠️ No grades data collected for {student_name}")
                    logging.warning(f"No grades data collected for {student_name}")
                    
            except Exception as e:
                print(f"❌ Error processing {student_name}: {str(e)}")
                logging.error(f"Error processing {student_name}: {str(e)}")
        
        # After all students are processed, generate the Notion-friendly CSV
        print("\n--- Generating Notion-friendly grades format ---")
        logging.info("Generating Notion-friendly grades format")
        
        # Track number of records before
        before_count = 0
        notion_grades_path = os.path.join("notion_processor", "data", "notion_grades.csv")
        if os.path.exists(notion_grades_path):
            with open(notion_grades_path, 'r') as f:
                before_count = sum(1 for _ in f) - 1  # Subtract header
        
        process_notion()
        
        # Calculate records added
        after_count = 0
        if os.path.exists(notion_grades_path):
            with open(notion_grades_path, 'r') as f:
                after_count = sum(1 for _ in f) - 1  # Subtract header
        
        records_added = max(0, after_count - before_count)
        
        end_time = datetime.now()
        duration = end_time - start_time
        print(f"\n--- Grades collection completed at {end_time} ---")
        print(f"--- Duration: {duration} ---")
        print(f"--- Students processed: {students_processed} ---")
        print(f"--- Records added: {records_added} ---\n")
        
        logging.info(f"Grades collection completed at {end_time}")
        logging.info(f"Duration: {duration}")
        logging.info(f"Students processed: {students_processed}")
        logging.info(f"Records added: {records_added}")
        
        # Send success notification
        email_notifier.send_success_notification(students_processed, records_added)
        
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(f"\n{error_message}")
        logging.error(error_message)
        
        # Send failure notification
        email_notifier.send_failure_notification(error_message)
        
        sys.exit(1)

if __name__ == "__main__":
    main()
