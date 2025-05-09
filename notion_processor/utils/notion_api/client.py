import pandas as pd
import os
import math
import numpy as np
from datetime import datetime
from notion_client import Client
from typing import Dict, Any, List, Optional

# Import configuration
from .config import (
    NOTION_API_KEY, 
    NOTION_DATABASE_ID, 
    NOTION_PROPERTY_MAP, 
    NOTION_PROPERTY_TYPES
)

class NotionClient:
    def __init__(self):
        """Initialize the Notion client with API key."""
        self.client = Client(auth=NOTION_API_KEY)
        self.database_id = NOTION_DATABASE_ID
        
    def _format_property_value(self, property_name: str, value: Any) -> Dict[str, Any]:
        """Format a property value according to its type in Notion."""
        property_type = NOTION_PROPERTY_TYPES.get(property_name)
        
        if value == "" or value is None or pd.isna(value) or (isinstance(value, str) and value.lower() == "n/a"):
            # Return empty/null value based on property type
            if property_type == "number":
                return {"number": None}
            elif property_type == "date":
                return {"date": None}
            elif property_type == "title":
                return {"title": []}
            elif property_type == "rich_text":
                return {"rich_text": []}
            elif property_type == "select":
                return {"select": None}
            else:
                return {"rich_text": []}
        
        # Format based on property type
        if property_type == "title":
            return {
                "title": [
                    {
                        "text": {
                            "content": str(value)
                        }
                    }
                ]
            }
        elif property_type == "rich_text":
            return {
                "rich_text": [
                    {
                        "text": {
                            "content": str(value)
                        }
                    }
                ]
            }
        elif property_type == "number":
            # Handle N/A values for number fields
            if isinstance(value, str) and (value == "N/A" or value.strip() == ""):
                return {"number": None}
            try:
                # Check for NaN, infinity, etc.
                float_value = float(value)
                if math.isnan(float_value) or math.isinf(float_value):
                    return {"number": None}
                return {"number": float_value}
            except (ValueError, TypeError):
                return {"number": None}
        elif property_type == "date":
            try:
                # Parse date if it's a string
                if isinstance(value, str):
                    dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                    date_string = dt.isoformat()
                else:
                    date_string = value.isoformat()
                
                return {
                    "date": {
                        "start": date_string,
                        "end": None
                    }
                }
            except (ValueError, TypeError, AttributeError):
                return {"date": None}
        elif property_type == "select":
            # Special handling for Is Latest Batch
            if property_name == "Is Latest Batch":
                if isinstance(value, bool):
                    return {"select": {"name": "True" if value else "False"}}
                elif isinstance(value, str):
                    return {"select": {"name": value}}
                else:
                    return {"select": {"name": str(value)}}
            else:
                # Normal select handling
                return {"select": {"name": str(value)}}
        else:
            # Default to rich_text for unknown types
            return {
                "rich_text": [
                    {
                        "text": {
                            "content": str(value)
                        }
                    }
                ]
            }
            
    def _prepare_page_properties(self, row: pd.Series) -> Dict[str, Dict]:
        """Prepare properties for a Notion page from a DataFrame row."""
        properties = {}
        
        for csv_column, notion_property in NOTION_PROPERTY_MAP.items():
            # Skip the Updated Time column as it will be handled by Notion's created_time
            if csv_column == "Updated Time":
                continue
                
            if csv_column in row.index:
                value = row[csv_column]
                properties[notion_property] = self._format_property_value(csv_column, value)
        
        return properties
        
    def get_existing_student_names(self) -> List[str]:
        """Get a list of student names already in the Notion database."""
        results = []
        has_more = True
        next_cursor = None
        
        while has_more:
            response = self.client.databases.query(
                database_id=self.database_id,
                start_cursor=next_cursor
            )
            
            for page in response["results"]:
                # Extract student name from the title property
                try:
                    student_name_property = page["properties"].get("student_name")
                    if student_name_property and student_name_property.get("title"):
                        title_content = student_name_property["title"]
                        if title_content and len(title_content) > 0:
                            student_name = title_content[0]["plain_text"]
                            results.append(student_name)
                except (KeyError, IndexError) as e:
                    print(f"Error extracting student name: {e}")
                    continue
            
            # Check if there are more pages to fetch
            has_more = response.get("has_more", False)
            next_cursor = response.get("next_cursor")
        
        return results
    
    def reset_latest_batch_flags(self) -> int:
        """
        Reset all 'Is Latest Batch' flags to False for existing records.
        Returns the number of records updated.
        """
        print("Resetting 'Is Latest Batch' flags for existing records...")
        updated_count = 0
        
        try:
            # Query records where Is Latest Batch is "True"
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Is Latest Batch",
                    "select": {
                        "equals": "True"
                    }
                }
            )
            
            # Update each record
            for page in response["results"]:
                page_id = page["id"]
                try:
                    self.client.pages.update(
                        page_id=page_id,
                        properties={
                            "Is Latest Batch": {"select": {"name": "False"}}
                        }
                    )
                    updated_count += 1
                except Exception as e:
                    print(f"⚠️ Error updating record {page_id}: {str(e)}")
                    continue
            
            print(f"✅ Reset {updated_count} 'Is Latest Batch' flags")
            return updated_count
            
        except Exception as e:
            print(f"⚠️ Error resetting 'Is Latest Batch' flags: {str(e)}")
            return 0
    
    def append_data_from_csv(self, csv_path: str) -> int:
        """
        Append data from a CSV file to the Notion database.
        Returns the number of records added.
        """
        if not os.path.exists(csv_path):
            print(f"⚠️ CSV file {csv_path} does not exist.")
            return 0
            
        try:
            # Read the CSV file
            df = pd.read_csv(csv_path)
            
            if df.empty:
                print(f"⚠️ No data found in {csv_path}")
                return 0
                
            # Count of added records
            added_count = 0
            
            # Process each row in the DataFrame
            for _, row in df.iterrows():
                student_name = row["student_name"]
                # Prepare page properties
                properties = self._prepare_page_properties(row)
                
                # Create a new page in the database
                try:
                    self.client.pages.create(
                        parent={"database_id": self.database_id},
                        properties=properties
                    )
                    added_count += 1
                    print(f"✅ Added student: {student_name}")
                except Exception as e:
                    print(f"⚠️ Error adding student {student_name}: {str(e)}")
                    continue
            
            return added_count
            
        except Exception as e:
            print(f"⚠️ Error processing CSV: {str(e)}")
            return 0
            
    def update_student_records(self, csv_path: str) -> int:
        """
        Append all student records from a CSV file to the Notion database.
        Always creates new entries for students regardless of whether they exist.
        Returns the number of records added.
        """
        if not os.path.exists(csv_path):
            print(f"⚠️ CSV file {csv_path} does not exist.")
            return 0
            
        try:
            # First, reset all 'Is Latest Batch' flags
            self.reset_latest_batch_flags()
            
            # Read the CSV file - handle N/A by converting them to NaN
            df = pd.read_csv(csv_path, na_values=['N/A', ''])
            
            # Replace NaN with None to avoid JSON serialization issues
            df = df.replace({np.nan: None})
            
            # Set 'Is Latest Batch' to True for all new records
            df['Is Latest Batch'] = True
            
            if df.empty:
                print(f"⚠️ No data found in {csv_path}")
                return 0
            
            # Count of added records
            added_count = 0
            
            # Always create new records for each row in the DataFrame
            for _, row in df.iterrows():
                student_name = row["student_name"]
                
                # Ensure student name fields are preserved and not None or empty strings
                # This fixes the issue with missing student_chinese_name and student_english_name
                if row.get("student_chinese_name") is None or str(row.get("student_chinese_name")).strip() == "":
                    print(f"⚠️ Missing Chinese name for student {student_name}")
                
                if row.get("student_english_name") is None or str(row.get("student_english_name")).strip() == "":
                    print(f"⚠️ Missing English name for student {student_name}")
                
                # Prepare properties for Notion
                properties = self._prepare_page_properties(row)
                
                # Create a new page in the database
                try:
                    self.client.pages.create(
                        parent={"database_id": self.database_id},
                        properties=properties
                    )
                    added_count += 1
                    print(f"✅ Added new record for student: {student_name}")
                except Exception as e:
                    print(f"⚠️ Error adding record for student {student_name}: {str(e)}")
            
            return added_count
            
        except Exception as e:
            print(f"⚠️ Error processing CSV: {str(e)}")
            return 0 