#!/usr/bin/env python3
"""
Notion processor for Canvas API data
Handles the formatting and exporting of Canvas data to Notion-compatible formats
"""

import os
import sys

# Add parent directory to sys.path to import from the project root
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the modules we need
from config import GRADES_CSV_PATH, NOTION_GRADES_CSV_PATH
from notion_processor.utils.notion_formatter import NotionFormatter

def process_for_notion():
    """Format and prepare data for Notion"""
    print("\n--- Starting Notion data processing ---")
    
    # Check if input file exists
    if not os.path.exists(GRADES_CSV_PATH):
        print(f"❌ Error: Input file {GRADES_CSV_PATH} not found")
        return False
    
    # Create Notion formatter
    formatter = NotionFormatter(GRADES_CSV_PATH, NOTION_GRADES_CSV_PATH)
    
    # Transform grades data to Notion format
    print("Transforming grades data to Notion format...")
    formatter.transform_long_to_wide()
    
    print("--- Notion data processing completed ---\n")
    return True

if __name__ == "__main__":
    process_for_notion() 