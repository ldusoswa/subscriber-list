from sensitive_data_config import *

import requests
import base64

access_token = None

# Encode the client ID and secret as a basic auth string
auth = base64.b64encode(f'{TWITCH_CLIENT_ID}:{TWITCH_CLIENT_SECRET}'.encode()).decode()

# Request an access token
headers = {
    'Authorization': f'Basic {auth}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

data = {
    'client_id': TWITCH_CLIENT_ID,
    'client_secret': TWITCH_CLIENT_SECRET,
    'grant_type': 'client_credentials',
    'scope': 'channel:read:subscriptions'
}

response = requests.post('https://id.twitch.tv/oauth2/token', headers=headers, data=data)

if response.status_code == 200:
    access_token = response.json()['access_token']
    print(f'Access token: {access_token}')
else:
    print(f'Error: {response.status_code} {response.json()["message"]}')
    print(f'Failed to get access token with error code {response.status_code}: {response.json()["error"]}')

import requests

headers = {
    'Authorization': f'Bearer {access_token}',
    'Client-ID': TWITCH_CLIENT_ID
}

response = requests.get(f'https://api.twitch.tv/helix/subscriptions?broadcaster_id={TWITCH_USER_ID}', headers=headers)

if response.status_code == 200:
    subscribers = response.json()['data']
    print(f'Subscribers: {subscribers}')
else:
    print(f'Failed to get subscribers with error code {response.status_code}: {response.json()["message"]}')
