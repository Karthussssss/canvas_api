from utils.credential_manager import CredentialManager
from data_collectors.grades import GradesCollector
from utils.csv_handler import CSVHandler
from notion_processor.notion_main import main as process_notion
from config import GRADES_CSV_PATH
import sys
import os

# Add the notion_processor directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "notion_processor"))

def collect_grades():
    """Collect grades for all students"""
    print("\n--- Starting grades collection ---\n")
    
    # Initialize credential manager
    manager = CredentialManager()
    
    # Initialize CSV handler
    csv_handler = CSVHandler(GRADES_CSV_PATH)
    
    # Get all student names
    student_names = manager.get_all_student_names()
    
    if not student_names:
        print("No students found in credentials file.")
        return
    
    print(f"Found {len(student_names)} students in credentials file.")
    
    # Process each student
    for student_name in student_names:
        print(f"\n=== Processing student: {student_name} ===\n")
        
        # Get student credentials
        credentials = manager.get_student_credentials(student_name)
        if not credentials:
            print(f"❌ No credentials found for {student_name}")
            continue
            
        # Make sure user_id is an integer
        user_id = credentials.get("user_id")
        if not user_id:
            print(f"❌ No user_id found for {student_name}")
            continue
            
        try:
            user_id = int(user_id)
        except ValueError:
            print(f"❌ Invalid user_id for {student_name}: {user_id}")
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
            else:
                print(f"\n⚠️ No grades data collected for {student_name}")
                
        except Exception as e:
            print(f"❌ Error processing {student_name}: {str(e)}")
    
    # After all students are processed, generate the Notion-friendly CSV
    print("\n--- Generating Notion-friendly grades format ---")
    process_notion()
    
    print("\n--- Grades collection completed ---")

def main():
    """Main entry point for Canvas API client."""
    
    print("\n--- Starting grades collection ---")
    
    try:
        # Create credential manager
        manager = CredentialManager()
        
        # Initialize CSV handler
        csv_handler = CSVHandler(GRADES_CSV_PATH)
        
        # Get all student names
        student_names = manager.get_all_student_names()
        
        if not student_names:
            print("No students found in credentials file.")
            return
        
        print(f"\nFound {len(student_names)} students in credentials file.\n")
        
        # Process each student
        for student_name in student_names:
            print(f"\n=== Processing student: {student_name} ===\n")
            
            # Get student credentials
            credentials = manager.get_student_credentials(student_name)
            if not credentials:
                print(f"❌ No credentials found for {student_name}")
                continue
                
            # Make sure user_id is an integer
            user_id = credentials.get("user_id")
            if not user_id:
                print(f"❌ No user_id found for {student_name}")
                continue
                
            try:
                user_id = int(user_id)
            except ValueError:
                print(f"❌ Invalid user_id for {student_name}: {user_id}")
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
                else:
                    print(f"\n⚠️ No grades data collected for {student_name}")
                    
            except Exception as e:
                print(f"❌ Error processing {student_name}: {str(e)}")
        
        # After all students are processed, generate the Notion-friendly CSV
        print("\n--- Generating Notion-friendly grades format ---")
        process_notion()
        
        print("\n--- Grades collection completed ---\n")
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
