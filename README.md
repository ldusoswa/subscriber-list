# Subscriber List Management System

Automates processing of membership data from YouTube, Twitch, and Patreon platforms.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Access (Automated Retrieval)

#### Twitch API

To automatically fetch Twitch subscribers without manual CSV downloads:

1. Create a Twitch application at https://dev.twitch.tv/console/apps
2. Add your Twitch credentials to `.env`:
   ```
   TWITCH_CLIENT_ID=your_client_id_here
   TWITCH_CLIENT_SECRET=your_client_secret_here
   TWITCH_REDIRECT_URI=https://www.yourwebsite.com
   ```
3. The channel ID will be auto-detected from your authenticated account

#### Patreon API

To automatically fetch Patreon members without manual CSV downloads:

1. Create a Patreon application at https://www.patreon.com/portal/registration/register-clients
2. Add your Patreon credentials to `.env`:
   ```
   PATREON_CLIENT_ID=your_client_id_here
   PATREON_CLIENT_SECRET=your_client_secret_here
   PATREON_REDIRECT_URI=https://www.yourwebsite.com
   ```

**First-time OAuth Setup:**
- On first run, a browser will open for authorization
- After authorizing, copy the code from the redirect URL
- Access tokens are cached (`.twitch_token.json`, `.patreon_token.json`) for future runs

### 3. Download YouTube CSV

- YouTube: Download "Your members" CSV to Downloads folder (API integration not yet implemented)

## Usage

```bash
python subtext.py
```

The script will:
1. **Automatically fetch** Twitch subscribers via API (no manual download needed!)
2. **Automatically fetch** Patreon members via API (no manual download needed!)
3. Load YouTube data from most recent CSV file
4. Generate reports and `levels.csv` for Photoshop import

## Fallback Mode

If API credentials are not configured, the script automatically falls back to loading from CSV files (old behavior) for each platform
