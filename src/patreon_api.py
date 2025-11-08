"""
Patreon API Integration
Handles OAuth authentication and member data retrieval from Patreon API.
"""
import os
import json
import webbrowser
import urllib.parse
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import requests


class PatreonAPI:
    """Manages Patreon API authentication and data retrieval"""
    
    TOKEN_FILE = '.patreon_token.json'
    AUTH_URL = 'https://www.patreon.com/oauth2/authorize'
    TOKEN_URL = 'https://www.patreon.com/api/oauth2/token'
    API_BASE_URL = 'https://www.patreon.com/api/oauth2/v2'
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize Patreon API client
        
        Args:
            client_id: Patreon application client ID
            client_secret: Patreon application client secret
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
                
                # Check if token is still valid (with 1 hour buffer)
                if datetime.now() < self.token_expiry - timedelta(hours=1):
                    print("Using cached Patreon access token")
                    return True
                elif self.refresh_token:
                    print("Patreon token expired, refreshing...")
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
        
        print(f"Patreon access token saved to {self.TOKEN_FILE}")
    
    def _refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token"""
        if not self.refresh_token:
            return False
        
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(self.TOKEN_URL, data=payload)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access_token')
            self.refresh_token = data.get('refresh_token', self.refresh_token)
            expires_in = data.get('expires_in', 0)
            
            if expires_in > 0:
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            self._save_token_to_file()
            print("Successfully refreshed Patreon access token")
            return True
        else:
            print(f"Failed to refresh token: {response.text}")
            return False
    
    def _get_authorization_code(self) -> str:
        """Open browser for OAuth authorization and get code from user"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'identity campaigns campaigns.members'
        }
        
        auth_url = f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"
        print('\n' + '='*80)
        print('PATREON AUTHORIZATION REQUIRED')
        print('='*80)
        print('Opening browser for Patreon authorization...')
        print(f'If browser does not open, visit: {auth_url}')
        print('='*80 + '\n')
        
        webbrowser.open(auth_url)
        
        code = input('After authorizing, paste the authorization code from the URL: ').strip()
        return code
    
    def _exchange_code_for_token(self, code: str) -> bool:
        """Exchange authorization code for access token"""
        payload = {
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri
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
            print("Successfully obtained Patreon access token")
            return True
        else:
            print(f"Failed to obtain access token: {response.text}")
            return False
    
    def authenticate(self) -> bool:
        """
        Authenticate with Patreon API
        Tries to use cached token first, otherwise initiates OAuth flow
        
        Returns:
            bool: True if authentication successful
        """
        # Try to load cached token
        if self._load_token_from_file():
            return True
        
        # Need to get new token
        print("Initiating Patreon OAuth flow...")
        code = self._get_authorization_code()
        
        if not code:
            print("No authorization code provided")
            return False
        
        return self._exchange_code_for_token(code)
    
    def get_campaign_id(self) -> Optional[str]:
        """
        Get the campaign ID for the authenticated user
        
        Returns:
            Campaign ID string or None if failed
        """
        if not self.access_token:
            return None
        
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        url = f'{self.API_BASE_URL}/campaigns'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            campaigns = data.get('data', [])
            if campaigns:
                campaign_id = campaigns[0].get('id')
                print(f"Found campaign ID: {campaign_id}")
                return campaign_id
        else:
            print(f"Failed to get campaign: {response.status_code} - {response.text}")
        
        return None
    
    def get_members(self) -> List[Dict]:
        """
        Fetch all members from Patreon API with pagination
        
        Returns:
            List of member dictionaries with user info and pledge details
        """
        if not self.access_token:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        campaign_id = self.get_campaign_id()
        if not campaign_id:
            raise RuntimeError("Failed to get campaign ID")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        all_members = []
        next_cursor = None
        
        print("Fetching Patreon members...")
        
        # Fields to include in the response
        fields = {
            'member': 'full_name,patron_status,currently_entitled_amount_cents,pledge_relationship_start',
            'tier': 'title,amount_cents'
        }
        
        while True:
            params = {
                'include': 'currently_entitled_tiers,user',
                'fields[member]': fields['member'],
                'fields[tier]': fields['tier']
            }
            
            if next_cursor:
                params['page[cursor]'] = next_cursor
            
            url = f'{self.API_BASE_URL}/campaigns/{campaign_id}/members'
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                raise RuntimeError(f"Failed to fetch members: {response.status_code} - {response.text}")
            
            data = response.json()
            members = data.get('data', [])
            included = data.get('included', [])
            
            # Build lookup for tiers and users
            tiers_map = {item['id']: item for item in included if item['type'] == 'tier'}
            users_map = {item['id']: item for item in included if item['type'] == 'user'}
            
            # Process members with their tier information
            for member in members:
                member_data = {
                    'member': member,
                    'tiers': [],
                    'user': None
                }
                
                # Get entitled tiers
                relationships = member.get('relationships', {})
                entitled_tiers = relationships.get('currently_entitled_tiers', {}).get('data', [])
                for tier_ref in entitled_tiers:
                    tier_id = tier_ref.get('id')
                    if tier_id in tiers_map:
                        member_data['tiers'].append(tiers_map[tier_id])
                
                # Get user info
                user_ref = relationships.get('user', {}).get('data', {})
                user_id = user_ref.get('id')
                if user_id in users_map:
                    member_data['user'] = users_map[user_id]
                
                all_members.append(member_data)
            
            # Check for more pages
            pagination = data.get('meta', {}).get('pagination', {})
            next_cursor = pagination.get('cursors', {}).get('next')
            
            if not next_cursor:
                break  # No more pages
        
        print(f"Retrieved {len(all_members)} Patreon members")
        return all_members
    
    def format_members_as_csv_rows(self, members: List[Dict]) -> List[List[str]]:
        """
        Format member data to match the expected CSV format
        
        Expected CSV columns based on PatreonProcessor.process_file():
        [0] name
        [1-7] various fields (not used in processing)
        [8] lifetime amount (used for sorting)
        [9] ? (not used)
        [10] tier name
        
        Returns:
            List of rows suitable for CSV writing
        """
        rows = []
        
        for member_data in members:
            member = member_data['member']
            attributes = member.get('attributes', {})
            
            # Get member name
            full_name = attributes.get('full_name', 'Unknown')
            
            # Get patron status
            patron_status = attributes.get('patron_status', '')
            
            # Skip if not an active patron
            if patron_status != 'active_patron':
                continue
            
            # Get currently entitled amount (in cents)
            entitled_amount_cents = attributes.get('currently_entitled_amount_cents', 0)
            entitled_amount = entitled_amount_cents / 100.0  # Convert to dollars/euros
            
            # Get pledge start date
            pledge_start = attributes.get('pledge_relationship_start', '')
            
            # Get tier name (use the highest tier if multiple)
            tier_name = ''
            tiers = member_data.get('tiers', [])
            if tiers:
                # Sort by amount and take the highest
                sorted_tiers = sorted(tiers, key=lambda t: t.get('attributes', {}).get('amount_cents', 0), reverse=True)
                tier_name = sorted_tiers[0].get('attributes', {}).get('title', '')
            
            # For lifetime amount, we'll use the current entitled amount as a proxy
            # The actual lifetime amount would require additional API calls
            lifetime_amount = entitled_amount
            
            # Build row matching expected format
            row = [
                full_name,           # [0] name
                '',                  # [1] unused
                '',                  # [2] unused
                '',                  # [3] unused
                '',                  # [4] unused
                '',                  # [5] unused
                '',                  # [6] unused
                '',                  # [7] unused
                str(lifetime_amount),# [8] lifetime amount for sorting
                '',                  # [9] unused
                tier_name            # [10] tier name
            ]
            
            rows.append(row)
        
        return rows


def get_patreon_members_programmatically(
    client_id: str,
    client_secret: str,
    redirect_uri: str
) -> List[List[str]]:
    """
    Convenience function to fetch Patreon members
    Automatically uses the authenticated user's campaign
    
    Args:
        client_id: Patreon application client ID
        client_secret: Patreon application client secret
        redirect_uri: OAuth redirect URI
    
    Returns:
        List of member rows in CSV format
    """
    api = PatreonAPI(client_id, client_secret, redirect_uri)
    
    if not api.authenticate():
        raise RuntimeError("Failed to authenticate with Patreon API")
    
    members = api.get_members()
    return api.format_members_as_csv_rows(members)
