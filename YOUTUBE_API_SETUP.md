# YouTube API Setup Guide

This guide will help you set up automatic fetching of YouTube members, so you don't need to manually download CSV files.

## Prerequisites

1. **Install required Python packages:**
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

## Setup Steps

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Name it something like "YouTube Member Tracker"
4. Click **"Create"**

### 2. Enable YouTube Data API v3

1. In your project, go to **"APIs & Services"** → **"Library"**
2. Search for **"YouTube Data API v3"**
3. Click on it and press **"Enable"**

### 3. Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. If prompted, configure the OAuth consent screen:
   - User Type: **External**
   - App name: "YouTube Member Tracker"
   - User support email: Your email
   - Developer contact: Your email
   - Click **"Save and Continue"** through the remaining steps
4. Back to Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: "YouTube Member Fetcher"
   - Click **"Create"**
5. Click **"Download JSON"** on the credentials you just created
6. Rename the downloaded file to `youtube_credentials.json`
7. Move it to your `subscriber-list` folder

### 4. Request YouTube Members API Access

⚠️ **IMPORTANT**: The Members API requires special approval from YouTube.

1. Go to [YouTube API Services Form](https://support.google.com/youtube/contact/yt_api_form)
2. Fill out the form:
   - **API Name**: YouTube Data API v3
   - **API Client ID**: (from your credentials)
   - **Describe your use case**: "Personal tool to manage and display my YouTube channel members in my livestreams"
3. Submit and wait for approval (can take a few days)

### 5. Enable Auto-Fetch in Your Script

Edit `subtext.py` and change this line:

```python
auto_fetch_youtube: bool = False  # Change to True
```

to:

```python
auto_fetch_youtube: bool = True
```

### 6. First Run Authentication

1. Run `python subtext.py`
2. A browser window will open asking you to authorize the app
3. Sign in with your YouTube account
4. Grant the requested permissions
5. The script will save a `youtube_token.json` file for future use

## Usage

Once set up, every time you run `subtext.py`:
- It will automatically fetch your latest YouTube members
- Save them to a CSV file in your Downloads folder
- Process them along with Twitch and Patreon data

## Troubleshooting

### "Members API not available"
- You need to wait for YouTube to approve your API access request
- Until then, continue downloading CSV files manually

### "Invalid credentials"
- Make sure `youtube_credentials.json` is in the correct folder
- Verify it's the OAuth 2.0 Desktop app credentials (not API key)

### "Token expired"
- Delete `youtube_token.json` and run the script again
- You'll need to re-authorize

## Alternative: Manual Download (Current Method)

If you prefer not to set up the API or are waiting for approval:
1. Go to YouTube Studio → Memberships
2. Click the download icon
3. Save to your Downloads folder
4. Run `subtext.py` as usual

## Files Created

- `youtube_credentials.json` - Your OAuth credentials (keep private!)
- `youtube_token.json` - Authentication token (auto-generated)
- `youtube_api.py` - The API integration code

## Security Notes

- **Never commit** `youtube_credentials.json` or `youtube_token.json` to Git
- These files contain sensitive authentication data
- They're already in `.gitignore`
