"""
YouTube Data API integration for fetching channel members
Requires: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""
import os
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_LIBS_AVAILABLE = True
except ImportError:
    GOOGLE_LIBS_AVAILABLE = False
    print("Warning: Google API libraries not installed.")
    print("Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")


class YouTubeMemberFetcher:
    """Fetches YouTube channel members using the YouTube Data API"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
    TOKEN_FILE = 'youtube_token.json'
    CREDENTIALS_FILE = 'youtube_credentials.json'
    
    def __init__(self, output_dir: str = '.'):
        self.output_dir = Path(output_dir)
        self.service = None
    
    def authenticate(self) -> bool:
        """Authenticate with YouTube API"""
        if not GOOGLE_LIBS_AVAILABLE:
            return False
        
        creds = None
        token_path = self.output_dir / self.TOKEN_FILE
        creds_path = self.output_dir / self.CREDENTIALS_FILE
        
        # Load existing token
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), self.SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not creds_path.exists():
                    print(f"\nError: {self.CREDENTIALS_FILE} not found!")
                    print("\nTo set up YouTube API access:")
                    print("1. Go to https://console.cloud.google.com/")
                    print("2. Create a new project or select existing")
                    print("3. Enable 'YouTube Data API v3'")
                    print("4. Create OAuth 2.0 credentials (Desktop app)")
                    print("5. Download the JSON file and save as 'youtube_credentials.json'")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next time
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('youtube', 'v3', credentials=creds)
        return True
    
    def fetch_members(self) -> List[Dict]:
        """Fetch all channel members"""
        if not self.service:
            print("Error: Not authenticated. Call authenticate() first.")
            return []
        
        members = []
        page_token = None
        
        try:
            while True:
                request = self.service.members().list(
                    part='snippet',
                    mode='all_current',
                    maxResults=1000,
                    pageToken=page_token
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    snippet = item['snippet']
                    member_details = snippet.get('memberDetails', {})
                    
                    member = {
                        'name': member_details.get('channelTitle', 'Unknown'),
                        'channel_id': member_details.get('channelId', ''),
                        'membership_level': snippet.get('membershipsDetails', {}).get('highestAccessibleLevel', 'Unknown'),
                        'membership_duration': snippet.get('membershipsDuration', {}).get('memberTotalDurationMonths', 0),
                        'since': snippet.get('membershipsDurationAtLevel', {}).get('memberSince', ''),
                    }
                    members.append(member)
                
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
                
                print(f"Fetched {len(members)} members so far...")
        
        except Exception as e:
            print(f"Error fetching members: {e}")
            print("\nNote: The Members API requires special access.")
            print("You may need to apply for access at: https://support.google.com/youtube/contact/yt_api_form")
        
        return members
    
    def save_to_csv(self, members: List[Dict], filename: Optional[str] = None) -> str:
        """Save members to CSV file in YouTube's export format"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"Your members {timestamp}.csv"
        
        output_path = self.output_dir / filename
        
        # Match YouTube's CSV format
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Header matching YouTube's export format
            writer.writerow([
                'Channel name',
                'Channel ID', 
                'Membership level',
                'Last updated (UTC)',
                'Total months as member',
                'Membership start date'
            ])
            
            for member in members:
                writer.writerow([
                    member['name'],
                    member['channel_id'],
                    member['membership_level'],
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    member['membership_duration'],
                    member['since']
                ])
        
        print(f"\n✓ Saved {len(members)} members to: {output_path}")
        return str(output_path)


def fetch_youtube_members(output_dir: str = '.') -> Optional[str]:
    """
    Main function to fetch YouTube members
    Returns the path to the created CSV file, or None if failed
    """
    if not GOOGLE_LIBS_AVAILABLE:
        print("\nCannot fetch YouTube members - required libraries not installed.")
        print("Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return None
    
    fetcher = YouTubeMemberFetcher(output_dir)
    
    print("Authenticating with YouTube...")
    if not fetcher.authenticate():
        return None
    
    print("Fetching channel members...")
    members = fetcher.fetch_members()
    
    if not members:
        print("No members found or unable to fetch members.")
        return None
    
    return fetcher.save_to_csv(members)


if __name__ == '__main__':
    # Test the fetcher
    result = fetch_youtube_members()
    if result:
        print(f"\nSuccess! Members saved to: {result}")
    else:
        print("\nFailed to fetch members.")
