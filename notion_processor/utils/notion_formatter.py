import csv
import os
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
import sys

# Ensure parent directory is in path to import from root
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now import from the parent project
from utils.error_handler import handle_file_error
from config import COURSE_NAME_TO_CHINESE

class NotionFormatter:
    def __init__(self, input_csv_path: str, output_csv_path: str):
        self.input_csv_path = input_csv_path
        self.output_csv_path = output_csv_path
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Ensure the directory for the output CSV file exists"""
        directory = os.path.dirname(self.output_csv_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in required format"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_all_possible_courses(self) -> List[str]:
        """Get all possible course names in Chinese from the config"""
        return list(COURSE_NAME_TO_CHINESE.values())

    def _get_course_chinese_to_english_map(self) -> Dict[str, str]:
        """Create a mapping from Chinese course names to English"""
        english_to_chinese = COURSE_NAME_TO_CHINESE
        chinese_to_english = {}
        
        # Create reverse mapping
        for english, chinese in english_to_chinese.items():
            # Extract the course name without the course code and semester info
            simplified_english = english.split(" - ")[0].strip()
            chinese_to_english[chinese] = simplified_english
            
        return chinese_to_english
        
    def transform_grades_for_notion(self) -> None:
        """Transform grades data into Notion-friendly format"""
        try:
            # Check if input file exists
            if not os.path.exists(self.input_csv_path):
                print(f"⚠️ Input file {self.input_csv_path} does not exist.")
                return
                
            # Read the grades CSV
            grades_df = pd.read_csv(self.input_csv_path)
            
            if grades_df.empty:
                print(f"⚠️ No data found in {self.input_csv_path}")
                return
                
            # Extract the latest data by grouping by student name and taking the latest fetch_time
            # This ensures we only get the most recent grades for each student and course
            grades_df['fetch_time'] = pd.to_datetime(grades_df['fetch_time'])
            latest_grades = grades_df.sort_values('fetch_time').groupby(['student_name', 'course_name']).last()
            latest_grades = latest_grades.reset_index()
            
            # Create a pivot table with students as rows and courses as columns
            # Use Chinese course names for column headers and include only scores (no grades)
            pivot_df = pd.pivot_table(
                latest_grades,
                index=['student_name', 'student_chinese_name', 'student_english_name'],
                columns='course_name_chinese',
                values=['score'],
                aggfunc='first'
            )
            
            # Flatten the multi-level column headers to make them Notion-friendly
            pivot_df.columns = [f"{col[1]}" for col in pivot_df.columns]
            
            # Reset index to make student names regular columns
            pivot_df = pivot_df.reset_index()
            
            # Add Updated Time column (will be added to the end by default)
            pivot_df['Updated Time'] = self._get_current_timestamp()
            
            # Save the transformed data to the Notion-friendly CSV
            pivot_df.to_csv(self.output_csv_path, index=False)
            
            print(f"✅ Successfully created Notion-friendly grades file at {self.output_csv_path}")
            print(f"   Format: {len(pivot_df)} students with {len(pivot_df.columns) - 4} course score columns")
            
        except Exception as e:
            handle_file_error(self.output_csv_path, "write", e)
            
    def transform_long_to_wide(self) -> None:
        """Transform long format to wide format for Notion and append to existing data"""
        try:
            # Read the grades CSV
            if not os.path.exists(self.input_csv_path):
                print(f"⚠️ Input file {self.input_csv_path} does not exist.")
                return
                
            grades_df = pd.read_csv(self.input_csv_path)
            
            if grades_df.empty:
                print(f"⚠️ No data found in {self.input_csv_path}")
                return
                
            # Get the most recent data from the input CSV
            grades_df['fetch_time'] = pd.to_datetime(grades_df['fetch_time'])
            latest_grades = grades_df.sort_values('fetch_time').drop_duplicates(
                subset=['student_name', 'course_name'], 
                keep='last'
            )
            
            # Get the latest fetch time for each student to use as a combined "Updated Time"
            latest_fetch_times = latest_grades.groupby('student_name')['fetch_time'].max()
            
            # Get all possible course names from config
            all_courses_chinese = self._get_all_possible_courses()
            
            # Get Chinese to English course name mapping
            chinese_to_english = self._get_course_chinese_to_english_map()
            
            # Prepare the new data
            new_data = []
            
            # Group by student
            for student_name, group in latest_grades.groupby('student_name'):
                row = {
                    'student_name': student_name,
                    'student_chinese_name': group['student_chinese_name'].iloc[0],
                    'student_english_name': group['student_english_name'].iloc[0],
                }
                
                # Initialize all course columns with None or N/A
                for course_name_chinese in all_courses_chinese:
                    course_name_english = chinese_to_english.get(course_name_chinese, course_name_chinese)
                    row[course_name_english] = "N/A"
                
                # Add each course's score (without grade) for courses the student is enrolled in
                for _, course_row in group.iterrows():
                    course_name_chinese = course_row['course_name_chinese']
                    course_name_english = chinese_to_english.get(course_name_chinese, course_name_chinese)
                    row[course_name_english] = course_row['score']
                
                # Add the Updated Time (will be moved to the end later)
                row['Updated Time'] = latest_fetch_times[student_name].strftime("%Y-%m-%d %H:%M:%S")
                
                new_data.append(row)
            
            # Create DataFrame for the new data
            new_df = pd.DataFrame(new_data)
            
            # Check if the output file exists and has data
            if os.path.exists(self.output_csv_path) and os.path.getsize(self.output_csv_path) > 0:
                # Read existing Notion grades CSV
                try:
                    existing_df = pd.read_csv(self.output_csv_path)
                    
                    # Remove the "未知课程" column if it exists
                    if "未知课程" in existing_df.columns:
                        existing_df = existing_df.drop(columns=["未知课程"])
                    
                    # Remove any Chinese column names and replace with English
                    columns_to_drop = []
                    for col in existing_df.columns:
                        if col in all_courses_chinese:
                            columns_to_drop.append(col)
                    
                    if columns_to_drop:
                        existing_df = existing_df.drop(columns=columns_to_drop)
                    
                    # Make sure the existing DataFrame has all course columns (in English)
                    for course_chinese in all_courses_chinese:
                        course_english = chinese_to_english.get(course_chinese, course_chinese)
                        if course_english not in existing_df.columns:
                            existing_df[course_english] = "N/A"
                    
                    # Make sure the new DataFrame has all columns from the existing DataFrame
                    for col in existing_df.columns:
                        if col not in new_df.columns and col not in ['student_name', 'student_chinese_name', 'student_english_name', 'Updated Time']:
                            new_df[col] = "N/A"
                    
                    # IMPORTANT: Remove duplicates from existing data before concatenating
                    # Remove existing entries for students that are in new_df to avoid duplication
                    students_to_update = new_df['student_name'].unique()
                    existing_df = existing_df[~existing_df['student_name'].isin(students_to_update)]
                    
                    # Append new data to existing data
                    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                    
                    # Move the Updated Time column to the end
                    if 'Updated Time' in combined_df.columns:
                        updated_time = combined_df.pop('Updated Time')
                        combined_df['Updated Time'] = updated_time
                    
                    # Save the combined data
                    combined_df.to_csv(self.output_csv_path, index=False)
                    
                    print(f"✅ Successfully appended new data to Notion grades file at {self.output_csv_path}")
                    print(f"   Added {len(new_df)} records to existing {len(existing_df)} records")
                except Exception as e:
                    print(f"⚠️ Error reading existing file, creating new one: {str(e)}")
                    
                    # Move the Updated Time column to the end for the new DataFrame
                    if 'Updated Time' in new_df.columns:
                        updated_time = new_df.pop('Updated Time')
                        new_df['Updated Time'] = updated_time
                        
                    new_df.to_csv(self.output_csv_path, index=False)
            else:
                # Move the Updated Time column to the end
                if 'Updated Time' in new_df.columns:
                    updated_time = new_df.pop('Updated Time')
                    new_df['Updated Time'] = updated_time
                
                # Save as a new file
                new_df.to_csv(self.output_csv_path, index=False)
                print(f"✅ Successfully created new Notion grades file at {self.output_csv_path}")
                
            # Count the number of course columns (excluding the 4 student info columns)
            course_columns = [col for col in new_df.columns if col not in ['student_name', 'student_chinese_name', 'student_english_name', 'Updated Time']]
            print(f"   Format: {len(new_df)} students with {len(course_columns)} course score columns")
            
        except Exception as e:
            handle_file_error(self.output_csv_path, "write", e) 