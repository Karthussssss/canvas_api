import logging
import sys
from typing import Optional, Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("canvas_api.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("canvas_api")

class CanvasAPIError(Exception):
    """Base class for Canvas API related errors"""
    pass

class CredentialError(CanvasAPIError):
    """Error related to missing or invalid credentials"""
    pass

class APIConnectionError(CanvasAPIError):
    """Error related to Canvas API connection"""
    pass

class DataProcessingError(CanvasAPIError):
    """Error related to processing data from Canvas API"""
    pass

class FileOperationError(CanvasAPIError):
    """Error related to file operations"""
    pass

def handle_credentials_error(student_id: str, error: Exception) -> None:
    """Handle errors related to student credentials"""
    logger.error(f"Credential error for student {student_id}: {str(error)}")
    raise CredentialError(f"Failed to load credentials for student {student_id}: {str(error)}")
    
def handle_api_error(student_id: str, endpoint: str, error: Exception) -> None:
    """Handle errors related to API calls"""
    logger.error(f"API error for student {student_id} at endpoint {endpoint}: {str(error)}")
    raise APIConnectionError(f"Failed to connect to Canvas API for student {student_id}: {str(error)}")

def handle_data_error(student_id: str, data_type: str, error: Exception) -> None:
    """Handle errors related to data processing"""
    logger.error(f"Data processing error for student {student_id}, data type {data_type}: {str(error)}")
    raise DataProcessingError(f"Failed to process {data_type} data for student {student_id}: {str(error)}")

def handle_file_error(file_path: str, operation: str, error: Exception) -> None:
    """Handle errors related to file operations"""
    logger.error(f"File operation error ({operation}) for {file_path}: {str(error)}")
    raise FileOperationError(f"Failed to {operation} file {file_path}: {str(error)}")
