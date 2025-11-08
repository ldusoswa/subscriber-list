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

#### YouTube API

To automatically fetch YouTube members without manual CSV downloads:

1. Create a Google Cloud project and enable YouTube Data API v3 at https://console.cloud.google.com/
2. Create OAuth 2.0 credentials (Desktop app type)
3. Add your YouTube credentials to `.env`:
   ```
   YOUTUBE_CLIENT_ID=your_client_id_here
   YOUTUBE_CLIENT_SECRET=your_client_secret_here
   YOUTUBE_REDIRECT_URI=http://localhost
   ```

**First-time OAuth Setup:**
- On first run, a browser will open for authorization
- After authorizing, copy the code from the redirect URL
- Access tokens are cached (`.twitch_token.json`, `.patreon_token.json`, `.youtube_token.json`) for future runs
- YouTube tokens include refresh tokens for long-term access

## Usage

```bash
python subtext.py
```

The script will:
1. **Automatically fetch** Twitch subscribers via API (no manual download needed!)
2. **Automatically fetch** Patreon members via API (no manual download needed!)
3. **Automatically fetch** YouTube members via API (no manual download needed!)
4. Generate reports and `levels.csv` for Photoshop import

## Fallback Mode

If API credentials are not configured, the script automatically falls back to loading from CSV files (old behavior) for each platform

## Photoshop Automation

Automate updating your Patreon Photoshop image with the latest subscriber data.

### Setup

1. **Create a Photoshop Action** (one-time setup):
   - Open Photoshop
   - Window > Actions
   - Create new action named "UpdatePatreon"
   - Record: Image > Variables > Data Sets > Import (select levels.csv)
   - Record: File > Export > Save for Web (save as Patreon6.jpg)
   - Stop recording
   
   See `ACTION_SETUP_GUIDE.md` for detailed step-by-step instructions.

2. Ensure your `Patreon6.psd` file is set up with data variables linked to `levels.csv`

### Usage

**Option 1: Full Automation (Recommended)**

Run the complete workflow that fetches data AND updates Photoshop:

```bash
python update_patreon_image.py
```

Or simply double-click: `update_patreon_image.bat`

**Option 2: Update Photoshop Only**

If you've already generated `levels.csv`, just update Photoshop:

```bash
python update_photoshop.py
```

### What It Does

1. Fetches latest subscriber data from YouTube, Twitch, and Patreon
2. Generates `levels.csv` with the updated data
3. Opens `Patreon6.psd` in Photoshop
4. Updates the data source with new CSV data
5. Exports as `Patreon6.jpg` using Save for Web settings
6. Closes the document

### Configuration

Edit `update_photoshop.py` to customize:
- **PSD_PATH**: Location of your PSD file (default: `C:\Users\dusosl\Dropbox\Youtube\Patreon6.psd`)
- **CSV_PATH**: Location of levels.csv (default: `c:\git\subscriber-list\levels.csv`)
- **OUTPUT_PATH**: Where to save the JPG (default: `C:\Users\dusosl\Dropbox\Youtube\Patreon6.jpg`)
- **JPEG_QUALITY**: Export quality 0-100 (default: 80)

### Requirements

- Adobe Photoshop must be installed
- Photoshop COM automation must be enabled (enabled by default)
- The PSD file should be set up with variables/data sets linked to CSV columns
