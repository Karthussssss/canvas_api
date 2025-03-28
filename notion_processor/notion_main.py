#!/usr/bin/env python3
"""
Notion processor for Canvas API data
Handles the formatting and exporting of Canvas data to Notion-compatible formats
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from notion_processor.utils.notion_formatter import NotionFormatter
from notion_processor.utils.notion_api.client import NotionClient

def main():
    """Main function to process grades data for Notion."""
    print("\n--- Starting Notion data processing ---")
    
    # Define file paths
    input_csv_path = os.path.join(parent_dir, "data", "grades.csv")
    output_csv_path = os.path.join(current_dir, "data", "notion_grades.csv")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    
    # Transform grades data to Notion format
    print("Transforming grades data to Notion format...")
    formatter = NotionFormatter(input_csv_path, output_csv_path)
    formatter.transform_long_to_wide()
    
    # Upload to Notion
    try:
        print("Appending data to Notion database...")
        notion_client = NotionClient()
        affected_count = notion_client.update_student_records(output_csv_path)
        print(f"✅ Successfully appended {affected_count} records to Notion database")
    except Exception as e:
        print(f"⚠️ Error uploading to Notion: {str(e)}")
    
    print("--- Notion data processing completed ---\n")

if __name__ == "__main__":
    main() 