import requests
import urllib.parse
import webbrowser

client_id = '2w0ydqjej94j5vhqck65wdtjjceu1o'
client_secret = 'swa2i0bw1lgxbnmjtqgzrfk9pnqgbn'
channel_id = '473785165'
scopes = ['channel:read:subscriptions']
redirect_uri = 'https://www.laurencedusoswa.com'

# Step 1: Get OAuth token

# Define the scope
scopes = ['channel:read:subscriptions']

# Step 1: Generate the Authorization URL and open it in the default web browser
base_url = 'https://id.twitch.tv/oauth2/authorize'
params = {
    'client_id': client_id,
    'redirect_uri': redirect_uri,
    'response_type': 'code',
    'scope': ' '.join(scopes)
}

auth_url = base_url + '?' + urllib.parse.urlencode(params)
print('Opening the following URL in the default web browser for authorization:')
print(auth_url)

# Open the URL in the default web browser
webbrowser.open(auth_url)

# Inform the user to enter the authorization code
code = input('Enter the authorization code: ')

# Step 2: Exchange Authorization Code for Access Token
url = 'https://id.twitch.tv/oauth2/token'
payload = {
    'client_id': client_id,
    'client_secret': client_secret,
    'code': code,
    'grant_type': 'authorization_code',
    'redirect_uri': redirect_uri
}

response = requests.post(url, params=payload)
token_data = response.json()
token = token_data.get('access_token')
print('Access Token:', token)

# Step 3: Validate the token
url = 'https://id.twitch.tv/oauth2/validate'
headers = {
    'Authorization': f'Bearer {token}'
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("Token is valid")
else:
    print("Token is invalid")
    exit()

# Step 4: Get subscribers
url = f'https://api.twitch.tv/helix/subscriptions?broadcaster_id={channel_id}'
headers = {
    'Client-ID': client_id,
    'Authorization': f'Bearer {token}'
}

response = requests.get(url, headers=headers)
subscribers = response.json()
print(subscribers)

# Print the list of subscribers
for subscriber in subscribers.get('data', []):
    print(subscriber['user_name'])
