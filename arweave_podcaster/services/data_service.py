"""
Data service for fetching and managing news data.

This module handles fetching news data from online sources and managing local data files.
"""

import requests
import urllib3
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..utils.config import config
from ..utils.file_utils import (
    save_json_file, load_json_file, ensure_directory_exists,
    get_date_folder_from_timestamp, find_most_recent_date_directory
)

# Suppress SSL warnings when verification is disabled
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DataService:
    """Service for managing news data fetching and storage."""
    
    def __init__(self, base_dir: str):
        """
        Initialize the data service.
        
        Args:
            base_dir: Base directory for the project
        """
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, 'data')
        ensure_directory_exists(self.data_dir)
    
    def fetch_online_news_data(self, url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch the latest Arweave Today JSON data from online source.
        
        Args:
            url: URL to fetch data from. If None, uses config.NEWS_SOURCE_URL
            
        Returns:
            Dictionary containing news data, or None if failed
        """
        if url is None:
            url = config.NEWS_SOURCE_URL
            
        try:
            print(f"🌐 Fetching latest news data from: {url}")
            
            # Try with SSL verification first
            try:
                response = requests.get(url, timeout=30, verify=True)
                response.raise_for_status()
            except requests.exceptions.SSLError:
                print("⚠️ SSL verification failed, retrying without SSL verification...")
                # Fallback without SSL verification
                response = requests.get(url, timeout=30, verify=False)
                response.raise_for_status()
            
            # Check if response is JSON
            content_type = response.headers.get('content-type', '').lower()
            if 'application/json' in content_type or url.endswith('.json'):
                # Direct JSON response
                news_data = response.json()
            else:
                # Might be HTML page, try to find JSON data or redirect
                print("🔍 Response is not JSON, checking for data...")
                news_data = self._try_alternative_endpoints(url)
                
                if not news_data:
                    print("❌ Could not find JSON data at any endpoint")
                    return None
            
            print("✅ Online news data fetched successfully!")
            return news_data
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Network error fetching news data: {e}")
            return None
        except Exception as e:
            print(f"⚠️ Error fetching news data: {e}")
            return None
    
    def _try_alternative_endpoints(self, base_url: str) -> Optional[Dict[str, Any]]:
        """
        Try alternative JSON endpoints when main URL doesn't return JSON.
        
        Args:
            base_url: Base URL to try variations of
            
        Returns:
            News data if found, None otherwise
        """
        json_urls = [
            base_url.rstrip('/') + '/data.json',
            base_url.rstrip('/') + '/today.json',
            base_url.rstrip('/') + '/api/today',
            config.GITHUB_FALLBACK_URL
        ]
        
        for json_url in json_urls:
            try:
                print(f"🔄 Trying: {json_url}")
                response = requests.get(json_url, timeout=30, verify=False)
                if response.status_code == 200:
                    news_data = response.json()
                    print(f"✅ Found JSON data at: {json_url}")
                    return news_data
            except Exception:
                continue
        
        return None
    
    def save_news_data_locally(self, news_data: Dict[str, Any]) -> bool:
        """
        Save news data to date-based directory structure.
        
        Args:
            news_data: News data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if 'ts' not in news_data:
                print("⚠️ No timestamp found in news data")
                return False
            
            timestamp_ms = news_data.get('ts', 0)
            date_folder = get_date_folder_from_timestamp(timestamp_ms)
            
            # Create date-based directory
            date_dir = os.path.join(self.data_dir, date_folder)
            ensure_directory_exists(date_dir)
            
            # Save in the date-based directory
            date_file_path = os.path.join(date_dir, 'today.json')
            if save_json_file(news_data, date_file_path):
                print(f"📅 News data saved in date directory: {date_folder}/today.json")
                return True
            return False
            
        except Exception as e:
            print(f"⚠️ Could not save news data locally: {e}")
            return False
    
    def load_local_news_data(self, date_folder: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Load news data from local file.
        
        Args:
            date_folder: Specific date folder to load from. If None, tries general location
            
        Returns:
            News data or None if not found
        """
        if date_folder:
            file_path = os.path.join(self.data_dir, date_folder, 'today.json')
        else:
            file_path = os.path.join(self.data_dir, 'today.json')
        
        return load_json_file(file_path)
    
    def get_most_recent_local_data(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent local news data from date directories.
        
        Returns:
            Most recent news data or None if not found
        """
        recent_file = find_most_recent_date_directory(self.data_dir)
        if recent_file:
            return load_json_file(recent_file)
        return None
    
    def load_news_data_smart(self, user_choice: str = "auto") -> Optional[Dict[str, Any]]:
        """
        Intelligently load news data based on user preference.
        
        Args:
            user_choice: 'online', 'local', or 'auto'
            
        Returns:
            News data or None if all sources fail
        """
        if user_choice == "online":
            return self._handle_online_choice()
        elif user_choice == "local":
            return self._handle_local_choice()
        else:  # auto
            return self._handle_auto_choice()
    
    def _handle_online_choice(self) -> Optional[Dict[str, Any]]:
        """Handle online data choice."""
        print("🌐 Fetching online data as requested...")
        news_data = self.fetch_online_news_data()
        if news_data:
            self.save_news_data_locally(news_data)
            return news_data
        else:
            print("❌ Failed to fetch online data.")
            print("💡 Would you like to try local data instead? (y/n)")
            try:
                fallback_choice = input().strip().lower()
                if fallback_choice in ['y', 'yes', '']:
                    print("🔄 Falling back to local data...")
                    return self._try_local_fallback()
            except KeyboardInterrupt:
                print("\n🛑 Operation cancelled.")
            return None
    
    def _handle_local_choice(self) -> Optional[Dict[str, Any]]:
        """Handle local data choice."""
        print("📁 Using local data as requested...")
        local_data = self.load_local_news_data()
        if local_data:
            return local_data
        else:
            print("⚠️ Standard local file not found, trying most recent date directory...")
            return self.get_most_recent_local_data()
    
    def _handle_auto_choice(self) -> Optional[Dict[str, Any]]:
        """Handle auto data choice."""
        print("🔄 Auto mode: Trying online first...")
        news_data = self.fetch_online_news_data()
        
        if news_data:
            self.save_news_data_locally(news_data)
            return news_data
        else:
            print("⚠️ Online fetch failed, trying local file...")
            return self._try_local_fallback()
    
    def _try_local_fallback(self) -> Optional[Dict[str, Any]]:
        """Try local data as fallback."""
        local_data = self.load_local_news_data()
        if local_data:
            print("✅ Using local data file.")
            return local_data
        else:
            print("⚠️ Local file failed, trying most recent date directory...")
            recent_data = self.get_most_recent_local_data()
            if recent_data:
                print("✅ Using most recent date directory data.")
                return recent_data
            else:
                print("❌ All data sources failed.")
                return None


def get_user_choice_for_data_source() -> str:
    """
    Get user's preference for data source.
    
    Returns:
        User choice string
    """
    print("\n" + "="*50)
    print("DATA SOURCE SELECTION")
    print("="*50)
    print("Choose your data source:")
    print("1. 🌐 Online (fetch latest from news source)")
    print("2. 📁 Local (use local today.json file)")
    print("3. 🔄 Auto (try online first, fallback to local)")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-3) [default: 3]: ").strip()
            
            if choice == '' or choice == '3':
                return "auto"
            elif choice == '1':
                return "online"
            elif choice == '2':
                return "local"
            else:
                print("⚠️  Invalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n🛑 Operation cancelled.")
            exit(1)
        except Exception as e:
            print(f"⚠️  Input error: {e}. Please try again.")


# Factory function
def create_data_service(base_dir: str) -> DataService:
    """
    Create a data service instance.
    
    Args:
        base_dir: Base directory for the project
        
    Returns:
        DataService instance
    """
    return DataService(base_dir)
