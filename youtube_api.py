"""
YouTube API Integration
Handles OAuth authentication and member data retrieval from YouTube API.
"""
import os
import json
import webbrowser
import urllib.parse
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import requests


class YouTubeAPI:
    """Manages YouTube API authentication and data retrieval"""
    
    TOKEN_FILE = '.youtube_token.json'
    AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
    TOKEN_URL = 'https://oauth2.googleapis.com/token'
    API_BASE_URL = 'https://www.googleapis.com/youtube/v3'
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize YouTube API client
        
        Args:
            client_id: Google OAuth client ID
            client_secret: Google OAuth client secret
            redirect_uri: OAuth redirect URI
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
    
    def _load_token_from_file(self) -> bool:
        """Load saved access token from file if it exists and is valid"""
        token_path = Path(self.TOKEN_FILE)
        if not token_path.exists():
            return False
        
        try:
            with open(token_path, 'r') as f:
                data = json.load(f)
            
            self.access_token = data.get('access_token')
            self.refresh_token = data.get('refresh_token')
            expiry_str = data.get('expiry')
            
            if self.access_token and expiry_str:
                self.token_expiry = datetime.fromisoformat(expiry_str)
                
                # Check if token is still valid (with 5 minute buffer)
                if datetime.now() < self.token_expiry - timedelta(minutes=5):
                    print("Using cached YouTube access token")
                    return True
                elif self.refresh_token:
                    print("YouTube token expired, refreshing...")
                    return self._refresh_access_token()
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error loading token file: {e}")
        
        return False
    
    def _save_token_to_file(self) -> None:
        """Save access token to file for reuse"""
        if not self.access_token:
            return
        
        data = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expiry': self.token_expiry.isoformat() if self.token_expiry else None
        }
        
        with open(self.TOKEN_FILE, 'w') as f:
            json.dump(data, f)
        
        print(f"YouTube access token saved to {self.TOKEN_FILE}")
    
    def _refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token"""
        if not self.refresh_token:
            return False
        
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(self.TOKEN_URL, data=payload)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access_token')
            # Refresh token is not returned in refresh response, keep existing one
            expires_in = data.get('expires_in', 0)
            
            if expires_in > 0:
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            self._save_token_to_file()
            print("Successfully refreshed YouTube access token")
            return True
        else:
            print(f"Failed to refresh token: {response.text}")
            return False
    
    def _get_authorization_code(self) -> str:
        """Open browser for OAuth authorization and get code from user"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'https://www.googleapis.com/auth/youtube.readonly',
            'access_type': 'offline',  # Request refresh token
            'prompt': 'consent'  # Force consent screen to get refresh token
        }
        
        auth_url = f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"
        print('\n' + '='*80)
        print('YOUTUBE AUTHORIZATION REQUIRED')
        print('='*80)
        print('Opening browser for YouTube authorization...')
        print(f'If browser does not open, visit: {auth_url}')
        print('='*80 + '\n')
        
        webbrowser.open(auth_url)
        
        code = input('After authorizing, paste the authorization code from the URL: ').strip()
        return code
    
    def _exchange_code_for_token(self, code: str) -> bool:
        """Exchange authorization code for access token"""
        payload = {
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(self.TOKEN_URL, data=payload)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access_token')
            self.refresh_token = data.get('refresh_token')
            expires_in = data.get('expires_in', 0)
            
            if expires_in > 0:
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            self._save_token_to_file()
            print("Successfully obtained YouTube access token")
            return True
        else:
            print(f"Failed to obtain access token: {response.text}")
            return False
    
    def authenticate(self) -> bool:
        """
        Authenticate with YouTube API
        Tries to use cached token first, otherwise initiates OAuth flow
        
        Returns:
            bool: True if authentication successful
        """
        # Try to load cached token
        if self._load_token_from_file():
            return True
        
        # Need to get new token
        print("Initiating YouTube OAuth flow...")
        code = self._get_authorization_code()
        
        if not code:
            print("No authorization code provided")
            return False
        
        return self._exchange_code_for_token(code)
    
    def get_channel_id(self) -> Optional[str]:
        """
        Get the channel ID for the authenticated user
        
        Returns:
            Channel ID string or None if failed
        """
        if not self.access_token:
            return None
        
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        params = {
            'part': 'id,snippet',
            'mine': 'true'
        }
        
        url = f'{self.API_BASE_URL}/channels'
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            if items:
                channel_id = items[0].get('id')
                channel_title = items[0].get('snippet', {}).get('title', 'Unknown')
                print(f"Authenticated as: {channel_title} (Channel ID: {channel_id})")
                return channel_id
        else:
            print(f"Failed to get channel: {response.status_code} - {response.text}")
        
        return None
    
    def get_members(self) -> List[Dict]:
        """
        Fetch all members from YouTube API with pagination
        
        Returns:
            List of member dictionaries with user info and membership details
        """
        if not self.access_token:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        channel_id = self.get_channel_id()
        if not channel_id:
            raise RuntimeError("Failed to get channel ID")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        all_members = []
        next_page_token = None
        
        print("Fetching YouTube members...")
        
        while True:
            params = {
                'part': 'snippet',
                'maxResults': 50,  # Max per page
                'hasAccessToLevel': 'any',
                'mode': 'all_current'
            }
            
            if next_page_token:
                params['pageToken'] = next_page_token
            
            url = f'{self.API_BASE_URL}/members'
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                raise RuntimeError(f"Failed to fetch members: {response.status_code} - {response.text}")
            
            data = response.json()
            members = data.get('items', [])
            all_members.extend(members)
            
            # Check for more pages
            next_page_token = data.get('nextPageToken')
            
            if not next_page_token:
                break  # No more pages
        
        print(f"Retrieved {len(all_members)} YouTube members")
        return all_members
    
    def format_members_as_csv_rows(self, members: List[Dict]) -> List[List[str]]:
        """
        Format member data to match the expected CSV format
        
        Expected CSV columns based on YouTubeProcessor.process_file():
        [0] name
        [1] ? (not used)
        [2] tier name
        [3] ? (not used)
        [4] total amount (used for sorting)
        
        Returns:
            List of rows suitable for CSV writing
        """
        rows = []
        
        for member in members:
            snippet = member.get('snippet', {})
            
            # Get member name
            member_details = snippet.get('memberDetails', {})
            display_name = member_details.get('displayName', 'Unknown')
            
            # Get membership level details
            memberships_details = snippet.get('membershipsDetails', {})
            
            # Get the highest level (first in list is usually the active one)
            highest_level = memberships_details.get('highestAccessibleLevel', '')
            highest_level_name = memberships_details.get('highestAccessibleLevelDisplayName', '')
            
            # Get membership duration
            member_since = memberships_details.get('memberSince', '')
            
            # Calculate total months (approximate from memberSince)
            total_months = 1
            if member_since:
                try:
                    since_date = datetime.fromisoformat(member_since.replace('Z', '+00:00'))
                    months_diff = (datetime.now(since_date.tzinfo) - since_date).days / 30
                    total_months = max(1, int(months_diff))
                except:
                    pass
            
            # Get tier information
            tier_name = highest_level_name
            
            # Estimate amount based on tier (this is approximate)
            # YouTube doesn't provide exact pricing in the API
            amount = 0.0
            if tier_name:
                # Try to extract amount from tier name or use defaults
                tier_lower = tier_name.lower()
                if 'boss' in tier_lower or '19.99' in tier_lower or '20' in tier_lower:
                    amount = 19.99
                elif 'chief' in tier_lower or '9.99' in tier_lower or '10' in tier_lower:
                    amount = 9.99
                elif 'crew' in tier_lower or '4.99' in tier_lower or '5' in tier_lower:
                    amount = 4.99
                else:
                    # Default to lowest tier
                    amount = 4.99
            
            # Calculate lifetime amount (approximate)
            lifetime_amount = amount * total_months
            
            # Build row matching expected format
            row = [
                display_name,              # [0] name
                '',                        # [1] unused
                tier_name,                 # [2] tier name
                '',                        # [3] unused
                str(lifetime_amount)       # [4] total amount for sorting
            ]
            
            rows.append(row)
        
        return rows


def get_youtube_members_programmatically(
    client_id: str,
    client_secret: str,
    redirect_uri: str
) -> List[List[str]]:
    """
    Convenience function to fetch YouTube members
    Automatically uses the authenticated user's channel
    
    Args:
        client_id: Google OAuth client ID
        client_secret: Google OAuth client secret
        redirect_uri: OAuth redirect URI
    
    Returns:
        List of member rows in CSV format
    """
    api = YouTubeAPI(client_id, client_secret, redirect_uri)
    
    if not api.authenticate():
        raise RuntimeError("Failed to authenticate with YouTube API")
    
    members = api.get_members()
    return api.format_members_as_csv_rows(members)
