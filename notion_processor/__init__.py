"""
Notion Processor Package
A package to handle the processing and formatting of data for Notion integration
"""

import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from .notion_main import main

__all__ = ['main'] 