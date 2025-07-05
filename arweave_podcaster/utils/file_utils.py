"""
File handling utilities for Arweave Podcaster.

This module contains functions for file operations, directory management, and data persistence.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional


def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
    """
    os.makedirs(directory_path, exist_ok=True)


def save_json_file(data: Dict[str, Any], file_path: str) -> bool:
    """
    Save dictionary data to a JSON file.
    
    Args:
        data: Dictionary to save
        file_path: Path where to save the file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        ensure_directory_exists(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"⚠️ Error saving JSON file {file_path}: {e}")
        return False


def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary data or None if failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ JSON file not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"⚠️ Error parsing JSON file {file_path}: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Error loading JSON file {file_path}: {e}")
        return None


def save_text_file(content: str, file_path: str) -> bool:
    """
    Save text content to a file.
    
    Args:
        content: Text content to save
        file_path: Path where to save the file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        ensure_directory_exists(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"💾 Text file saved: {os.path.basename(file_path)}")
        return True
    except Exception as e:
        print(f"⚠️ Error saving text file {file_path}: {e}")
        return False


def load_text_file(file_path: str) -> Optional[str]:
    """
    Load text content from a file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        Text content or None if failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"⚠️ Text file not found: {file_path}")
        return None
    except Exception as e:
        print(f"⚠️ Error loading text file {file_path}: {e}")
        return None


def get_date_folder_from_timestamp(timestamp_ms: int) -> str:
    """
    Get date folder name from timestamp.
    
    Args:
        timestamp_ms: Timestamp in milliseconds
        
    Returns:
        Date folder string in DD-MM-YYYY format
    """
    pub_date = datetime.fromtimestamp(timestamp_ms / 1000)
    return pub_date.strftime('%d-%m-%Y')


def get_formatted_date_from_timestamp(timestamp_ms: int) -> str:
    """
    Get formatted date string from timestamp.
    
    Args:
        timestamp_ms: Timestamp in milliseconds
        
    Returns:
        Formatted date string
    """
    pub_date = datetime.fromtimestamp(timestamp_ms / 1000)
    return pub_date.strftime('%B %d, %Y')


def get_datestamp_from_timestamp(timestamp_ms: int) -> str:
    """
    Get datestamp for filename from timestamp.
    
    Args:
        timestamp_ms: Timestamp in milliseconds
        
    Returns:
        Datestamp string in YYYY-MM-DD format
    """
    pub_date = datetime.fromtimestamp(timestamp_ms / 1000)
    return pub_date.strftime('%Y-%m-%d')


def find_most_recent_date_directory(base_data_dir: str) -> Optional[str]:
    """
    Find the most recent date directory in the data folder.
    
    Args:
        base_data_dir: Base data directory path
        
    Returns:
        Path to the most recent today.json file, or None if not found
    """
    try:
        if not os.path.exists(base_data_dir):
            return None
            
        # Get all directories that match the date format
        date_dirs = []
        for item in os.listdir(base_data_dir):
            item_path = os.path.join(base_data_dir, item)
            if os.path.isdir(item_path):
                # Check if it matches DD-MM-YYYY format
                try:
                    datetime.strptime(item, '%d-%m-%Y')
                    today_json_path = os.path.join(item_path, 'today.json')
                    if os.path.exists(today_json_path):
                        date_dirs.append((item, today_json_path))
                except ValueError:
                    continue
        
        if not date_dirs:
            return None
            
        # Sort by date (newest first)
        date_dirs.sort(key=lambda x: datetime.strptime(x[0], '%d-%m-%Y'), reverse=True)
        most_recent = date_dirs[0][1]
        print(f"📅 Found most recent data: {date_dirs[0][0]}/today.json")
        return most_recent
        
    except Exception as e:
        print(f"⚠️ Error finding recent date directory: {e}")
        return None


def create_output_filename(base_name: str, datestamp: str, extension: str) -> str:
    """
    Create standardized output filename.
    
    Args:
        base_name: Base name for the file (e.g., "ArweaveToday")
        datestamp: Date stamp in YYYY-MM-DD format
        extension: File extension (with or without dot)
        
    Returns:
        Complete filename
    """
    if not extension.startswith('.'):
        extension = '.' + extension
    return f"{base_name}-{datestamp}{extension}"
