# Subscriber List Management System

Automates processing of membership data from YouTube, Twitch, and Patreon platforms.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Twitch API (Automated Retrieval)

To automatically fetch Twitch subscribers without manual CSV downloads:

1. Create a Twitch application at https://dev.twitch.tv/console/apps
2. Copy `.env.example` to `.env`
3. Add your Twitch credentials to `.env`:
   ```
   TWITCH_CLIENT_ID=your_client_id_here
   TWITCH_CLIENT_SECRET=your_client_secret_here
   ```
4. The channel ID will be auto-detected from your authenticated account

**First-time OAuth Setup:**
- On first run, a browser will open for Twitch authorization
- After authorizing, copy the code from the redirect URL
- The access token is cached in `.twitch_token.json` for future runs

### 3. Download Other Platform CSVs

- YouTube: Download "Your members" CSV to Downloads folder
- Patreon: Download "Members_" CSV to Downloads folder

## Usage

```bash
python subtext.py
```

The script will:
1. **Automatically fetch** Twitch subscribers via API (no manual download needed!)
2. Load YouTube and Patreon data from most recent CSV files
3. Generate reports and `levels.csv` for Photoshop import

## Fallback Mode

If Twitch API credentials are not configured, the script automatically falls back to loading from CSV files (old behavior)
