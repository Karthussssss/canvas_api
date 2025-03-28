# Notion API Configuration
NOTION_API_KEY = "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"
NOTION_DATABASE_ID = "1c49efeede7b801b8c8fe08440084dff"

# Column mapping from CSV to Notion properties
# This maps the CSV headers to the corresponding Notion property names
NOTION_PROPERTY_MAP = {
    "student_name": "student_name",
    "student_chinese_name": "student_chinese_name",
    "student_english_name": "student_english_name",
    "Calculus 3A": "Calculus 3A",
    "Calculus 3B": "Calculus 3B",
    "Introduction to Statistics": "Introduction to Statistics",
    "Precalculus": "Precalculus",
    "General Biology": "General Biology",
    "General Psychology": "General Psychology",
    "Music Appreciation": "Music Appreciation",
    "Principles of Economics-Micro": "Principles of Economics-Micro",
    "Update Batch": "Update Batch"
    # Updated Time is removed as it will be handled by Notion's created_time
}

# Notion property types for each column
# This specifies the data type for each Notion property
NOTION_PROPERTY_TYPES = {
    "student_name": "title",
    "student_chinese_name": "rich_text",
    "student_english_name": "rich_text",
    "Calculus 3A": "number",
    "Calculus 3B": "number",
    "Introduction to Statistics": "number",
    "Precalculus": "number",
    "General Biology": "number",
    "General Psychology": "number",
    "Music Appreciation": "number",
    "Principles of Economics-Micro": "number",
    "Update Batch": "rich_text"
    # Updated Time is removed as it will be handled by Notion's created_time
} 