import requests

# Replace YOUR_CLIENT_ID with your actual client ID
client_id = '2w0ydqjej94j5vhqck65wdtjjceu1o'

# Replace YOUR_OAUTH_TOKEN with your actual OAuth token
oauth_token = {"access_token": "2o01gzr0mtkzm5zbpokzvjd7rjh9t6","expires_in": 13913,"refresh_token": "53361t7ogmm1uxho0nt6qh0i9cu7uy6nksg5erglmo1dvc4tj6","scope": ["channel:read:subscriptions"],"token_type": "bearer"}

# Replace YOUR_USERNAME with your actual Twitch username
username = 'LDusoswa'

# Set the URL for the API endpoint
url = 'https://api.twitch.tv/helix/subscriptions?broadcaster_id=' + username

# Set the headers for the API request
headers = {
    'Client-ID': client_id,
    'Authorization': f'Bearer {oauth_token}'
}

# Make the API request
response = requests.get(url, headers=headers)

print(headers)
print(response.status_code)
# Check the status code of the response
if response.status_code == 200:
    # Get the list of subscribers from the response
    subscribers = response.json()['data']

    # Print the list of subscribers
    for subscriber in subscribers:
        print(subscriber['user_name'])
else:
    # Print an error message if the request fails
    print('Error: Could not get list of subscribers')