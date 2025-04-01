#!/usr/bin/env python3
import pandas as pd
import os
import sys
from config import STUDENT_TO_CHINESE_NAME, STUDENT_TO_PREFERRED_ENGLISH_NAME, NOTION_GRADES_CSV_PATH

def update_student_names():
    """Update missing student names in the Notion grades CSV file"""
    print("Updating student names in Notion grades CSV...")
    
    if not os.path.exists(NOTION_GRADES_CSV_PATH):
        print(f"Error: {NOTION_GRADES_CSV_PATH} not found")
        return False
    
    try:
        # Read the Notion grades CSV
        df = pd.read_csv(NOTION_GRADES_CSV_PATH)
        
        # Count missing values before update
        missing_chinese_before = df['student_chinese_name'].isna().sum() + (df['student_chinese_name'] == '').sum()
        missing_english_before = df['student_english_name'].isna().sum() + (df['student_english_name'] == '').sum()
        
        # Create a backup just in case
        backup_path = f"{NOTION_GRADES_CSV_PATH}.bak"
        df.to_csv(backup_path, index=False)
        print(f"Created backup at {backup_path}")
        
        # Update the missing names
        for idx, row in df.iterrows():
            student_name = row['student_name']
            
            # Check if Chinese name is missing and can be updated
            if (pd.isna(row['student_chinese_name']) or row['student_chinese_name'] == '') and student_name in STUDENT_TO_CHINESE_NAME:
                df.at[idx, 'student_chinese_name'] = STUDENT_TO_CHINESE_NAME[student_name]
                print(f"Updated Chinese name for {student_name}: {STUDENT_TO_CHINESE_NAME[student_name]}")
            
            # Check if English name is missing and can be updated
            if (pd.isna(row['student_english_name']) or row['student_english_name'] == '') and student_name in STUDENT_TO_PREFERRED_ENGLISH_NAME:
                df.at[idx, 'student_english_name'] = STUDENT_TO_PREFERRED_ENGLISH_NAME[student_name]
                print(f"Updated English name for {student_name}: {STUDENT_TO_PREFERRED_ENGLISH_NAME[student_name]}")
        
        # Save the updated CSV
        df.to_csv(NOTION_GRADES_CSV_PATH, index=False)
        
        # Count missing values after update
        missing_chinese_after = df['student_chinese_name'].isna().sum() + (df['student_chinese_name'] == '').sum()
        missing_english_after = df['student_english_name'].isna().sum() + (df['student_english_name'] == '').sum()
        
        print(f"Before update: {missing_chinese_before} missing Chinese names, {missing_english_before} missing English names")
        print(f"After update: {missing_chinese_after} missing Chinese names, {missing_english_after} missing English names")
        print(f"Fixed {missing_chinese_before - missing_chinese_after} Chinese names and {missing_english_before - missing_english_after} English names")
        
        return True
    
    except Exception as e:
        print(f"Error updating student names: {str(e)}")
        return False

if __name__ == "__main__":
    update_student_names() 