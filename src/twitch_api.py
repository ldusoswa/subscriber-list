"""
Twitch API Integration
Handles OAuth authentication and subscriber data retrieval from Twitch API.
"""
import os
import json
import webbrowser
import urllib.parse
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import requests


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler to capture OAuth callback"""
    
    authorization_code = None
    
    def do_GET(self):
        """Handle GET request from OAuth redirect"""
        # Parse the query parameters
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        # Extract the authorization code
        if 'code' in params:
            OAuthCallbackHandler.authorization_code = params['code'][0]
            message = "Authorization successful! You can close this window."
            self.send_response(200)
        else:
            message = "Authorization failed. No code received."
            self.send_response(400)
        
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"""
            <html>
            <head><title>Twitch OAuth</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>{message}</h1>
                <p>Returning to application...</p>
            </body>
            </html>
        """.encode())
    
    def log_message(self, format, *args):
        """Suppress server log messages"""
        pass


class TwitchAPI:
    """Manages Twitch API authentication and data retrieval"""
    
    TOKEN_FILE = '.twitch_token.json'
    AUTH_URL = 'https://id.twitch.tv/oauth2/authorize'
    TOKEN_URL = 'https://id.twitch.tv/oauth2/token'
    VALIDATE_URL = 'https://id.twitch.tv/oauth2/validate'
    SUBSCRIPTIONS_URL = 'https://api.twitch.tv/helix/subscriptions'
    USERS_URL = 'https://api.twitch.tv/helix/users'
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize Twitch API client
        
        Args:
            client_id: Twitch application client ID
            client_secret: Twitch application client secret
            redirect_uri: OAuth redirect URI
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token: Optional[str] = None
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
            expiry_str = data.get('expiry')
            
            if self.access_token and expiry_str:
                self.token_expiry = datetime.fromisoformat(expiry_str)
                
                # Check if token is still valid (with 1 hour buffer)
                if datetime.now() < self.token_expiry - timedelta(hours=1):
                    print("Using cached Twitch access token")
                    return True
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error loading token file: {e}")
        
        return False
    
    def _save_token_to_file(self) -> None:
        """Save access token to file for reuse"""
        if not self.access_token or not self.token_expiry:
            return
        
        data = {
            'access_token': self.access_token,
            'expiry': self.token_expiry.isoformat()
        }
        
        with open(self.TOKEN_FILE, 'w') as f:
            json.dump(data, f)
        
        print(f"Twitch access token saved to {self.TOKEN_FILE}")
    
    def _validate_token(self) -> bool:
        """Validate the current access token"""
        if not self.access_token:
            return False
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(self.VALIDATE_URL, headers=headers)
        
        if response.status_code == 200:
            # Update expiry based on validation response
            data = response.json()
            expires_in = data.get('expires_in', 0)
            if expires_in > 0:
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            return True
        
        return False
    
    def _get_authorization_code(self) -> str:
        """Open browser for OAuth authorization and automatically capture code"""
        # Check if redirect_uri is localhost
        if 'localhost' in self.redirect_uri or '127.0.0.1' in self.redirect_uri:
            return self._get_code_with_local_server()
        else:
            return self._get_code_manual()
    
    def _get_code_with_local_server(self) -> str:
        """Start local server and automatically capture OAuth code"""
        # Parse port from redirect_uri or use default
        parsed = urllib.parse.urlparse(self.redirect_uri)
        port = parsed.port or 8080
        
        # Reset the authorization code
        OAuthCallbackHandler.authorization_code = None
        
        # Start local HTTP server
        server = HTTPServer(('localhost', port), OAuthCallbackHandler)
        server_thread = Thread(target=server.handle_request, daemon=True)
        server_thread.start()
        
        # Build authorization URL
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'channel:read:subscriptions'
        }
        
        auth_url = f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"
        print('\n' + '='*80)
        print('TWITCH AUTHORIZATION REQUIRED')
        print('='*80)
        print('Opening browser for Twitch authorization...')
        print(f'Waiting for authorization on http://localhost:{port}')
        print('='*80 + '\n')
        
        webbrowser.open(auth_url)
        
        # Wait for the callback
        server_thread.join(timeout=120)  # 2 minute timeout
        server.server_close()
        
        if OAuthCallbackHandler.authorization_code:
            print("✓ Authorization code received automatically")
            return OAuthCallbackHandler.authorization_code
        else:
            raise RuntimeError("Failed to receive authorization code. Please try again.")
    
    def _get_code_manual(self) -> str:
        """Fallback: manually get code from user"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'channel:read:subscriptions'
        }
        
        auth_url = f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"
        print('\n' + '='*80)
        print('TWITCH AUTHORIZATION REQUIRED')
        print('='*80)
        print('Opening browser for Twitch authorization...')
        print(f'If browser does not open, visit: {auth_url}')
        print('='*80 + '\n')
        
        webbrowser.open(auth_url)
        
        code = input('After authorizing, paste the authorization code from the URL: ').strip()
        return code
    
    def _exchange_code_for_token(self, code: str) -> bool:
        """Exchange authorization code for access token"""
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(self.TOKEN_URL, data=payload)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access_token')
            expires_in = data.get('expires_in', 0)
            
            if expires_in > 0:
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            self._save_token_to_file()
            print("Successfully obtained Twitch access token")
            return True
        else:
            print(f"Failed to obtain access token: {response.text}")
            return False
    
    def authenticate(self) -> bool:
        """
        Authenticate with Twitch API
        Tries to use cached token first, otherwise initiates OAuth flow
        
        Returns:
            bool: True if authentication successful
        """
        # Try to load cached token
        if self._load_token_from_file():
            if self._validate_token():
                return True
            print("Cached token is invalid or expired")
        
        # Need to get new token
        print("Initiating Twitch OAuth flow...")
        code = self._get_authorization_code()
        
        if not code:
            print("No authorization code provided")
            return False
        
        return self._exchange_code_for_token(code)
    
    def get_authenticated_user_id(self) -> Optional[str]:
        """
        Get the user ID of the authenticated user
        This is useful when the channel_id in config doesn't match the OAuth token
        
        Returns:
            User ID string or None if failed
        """
        if not self.access_token:
            return None
        
        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}'
        }
        
        response = requests.get(self.USERS_URL, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            users = data.get('data', [])
            if users:
                user_id = users[0].get('id')
                login = users[0].get('login')
                print(f"Authenticated as: {login} (ID: {user_id})")
                return user_id
        
        return None
    
    def get_subscribers(self) -> List[Dict]:
        """
        Fetch all subscribers from Twitch API with pagination
        Uses the authenticated user's ID as the broadcaster
        
        Returns:
            List of subscriber dictionaries with user info and subscription details
        """
        if not self.access_token:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        # Always use authenticated user's ID
        broadcaster_id = self.get_authenticated_user_id()
        if not broadcaster_id:
            raise RuntimeError("Failed to get authenticated user ID")
        
        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}'
        }
        
        all_subscribers = []
        pagination_cursor = None
        
        print("Fetching Twitch subscribers...")
        
        while True:
            params = {
                'broadcaster_id': broadcaster_id,
                'first': 100  # Max per page
            }
            
            if pagination_cursor:
                params['after'] = pagination_cursor
            
            response = requests.get(self.SUBSCRIPTIONS_URL, headers=headers, params=params)
            
            if response.status_code != 200:
                raise RuntimeError(f"Failed to fetch subscribers: {response.status_code} - {response.text}")
            
            data = response.json()
            subscribers = data.get('data', [])
            all_subscribers.extend(subscribers)
            
            # Check for more pages
            pagination = data.get('pagination', {})
            pagination_cursor = pagination.get('cursor')
            
            if not pagination_cursor:
                break  # No more pages
        
        print(f"Retrieved {len(all_subscribers)} Twitch subscribers")
        return all_subscribers
    
    def format_subscribers_as_csv_rows(self, subscribers: List[Dict]) -> List[List[str]]:
        """
        Format subscriber data to match the expected CSV format
        
        Expected CSV columns based on TwitchProcessor.process_file():
        [0] username
        [1] subscription date (ISO format)
        [2] ? (not used in processing)
        [3] ? (used for sorting - appears to be total months or amount)
        [4] ? (not used)
        [5] subscription type ('gift', 'prime', or regular)
        
        Returns:
            List of rows suitable for CSV writing
        """
        rows = []
        
        for sub in subscribers:
            username = sub.get('user_name', '')
            user_login = sub.get('user_login', '')
            
            # Filter out self-subscription (ldusoswa)
            if user_login.lower() == 'ldusoswa' or username.lower() == 'ldusoswa':
                continue
            
            # Determine subscription type
            is_gift = sub.get('is_gift', False)
            tier = sub.get('tier', '1000')  # Default to tier 1
            
            # Map tier to readable format (1000 = Tier 1, 2000 = Tier 2, 3000 = Tier 3)
            tier_name = f"Tier {int(tier) // 1000}"
            
            # Check if it's a Prime subscription (Twitch API doesn't directly indicate this)
            # We'll mark as 'prime' if tier is 'Prime' or if indicated in the data
            sub_type = 'gift' if is_gift else 'paid'
            
            # For sorting: use total months subscribed or default to 1
            # Note: Twitch API doesn't always provide cumulative months in subscriptions endpoint
            # You may need to use a different endpoint or accept this limitation
            total_months = 1  # Default value
            
            # Get subscription date - this might not be available in all API responses
            # The subscriptions endpoint doesn't always include the original subscription date
            # We'll use current time as a fallback
            sub_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # Build row matching expected format
            row = [
                user_login or username,  # [0] username
                sub_date,                # [1] subscription date
                '',                      # [2] unused
                str(total_months),       # [3] for sorting
                '',                      # [4] unused
                sub_type                 # [5] subscription type
            ]
            
            rows.append(row)
        
        return rows


def get_twitch_subscribers_programmatically(
    client_id: str,
    client_secret: str,
    redirect_uri: str
) -> List[List[str]]:
    """
    Convenience function to fetch Twitch subscribers
    Automatically uses the authenticated user's channel
    
    Args:
        client_id: Twitch application client ID
        client_secret: Twitch application client secret
        redirect_uri: OAuth redirect URI
    
    Returns:
        List of subscriber rows in CSV format
    """
    api = TwitchAPI(client_id, client_secret, redirect_uri)
    
    if not api.authenticate():
        raise RuntimeError("Failed to authenticate with Twitch API")
    
    subscribers = api.get_subscribers()
    return api.format_subscribers_as_csv_rows(subscribers)
