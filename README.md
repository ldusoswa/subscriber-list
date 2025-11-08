# Subscriber List Management System

Automates processing of membership data from YouTube, Twitch, and Patreon platforms, and updates Photoshop graphics with the latest data.

## Features

- 🔄 **Automated Data Fetching**: Pulls subscriber/member data from YouTube, Twitch, and Patreon APIs
- 📊 **CSV Generation**: Creates formatted CSV files for analysis and Photoshop import
- 🎨 **Photoshop Automation**: Automatically updates PSD files and exports JPG images
- 🚀 **One-Click Workflow**: Complete automation from data fetch to image export

## Repository Structure

```
subscriber-list/
├── src/                          # Source code
│   ├── subtext.py                # Main script: fetches data and generates CSV
│   ├── youtube_api.py            # YouTube API integration
│   ├── twitch_api.py             # Twitch API integration
│   ├── patreon_api.py            # Patreon API integration
│   ├── length.py                 # Utility functions
│   └── twitch.py                 # Legacy Twitch integration
├── scripts/                      # Automation scripts
│   ├── update_patreon_image.py   # Full automation workflow
│   ├── update_photoshop.py       # Photoshop automation script
│   ├── trigger_action.jsx        # JSX script to trigger Photoshop action
│   ├── update_patreon_image.bat  # Windows batch launcher
│   ├── UpdatePatreon.vbs         # VBS wrapper for taskbar shortcut
│   └── install_dependencies.bat  # Dependency installer
├── data/                         # Generated data files (gitignored)
│   ├── levels.csv                # Formatted data for Photoshop
│   ├── all_members.csv           # Combined member data
│   └── *.csv                     # Other generated reports
├── requirements.txt              # Python dependencies
├── .env                          # API credentials (not in repo)
└── README.md                     # This file
```

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
python src/subtext.py
```

The script will:
1. **Automatically fetch** Twitch subscribers via API (no manual download needed!)
2. **Automatically fetch** Patreon members via API (no manual download needed!)
3. **Automatically fetch** YouTube members via API (no manual download needed!)
4. Generate reports and `data/levels.csv` for Photoshop import

## Fallback Mode

If API credentials are not configured, the script automatically falls back to loading from CSV files (old behavior) for each platform

## Photoshop Automation

Automates updating Photoshop PSD files with the latest subscriber data and exports JPG images.

### One-Time Setup

#### 1. Configure Your PSD File

Set up your `Patreon6.psd` with variables linked to CSV columns:
- **Image > Variables > Define** to create text variables
- Link each variable to a CSV column name
- Save the PSD file

#### 2. Create Photoshop Action

1. Open Photoshop
2. **Window > Actions** (or press Alt+F9)
3. Click **New Action**:
   - Name: `UpdatePatreon`
   - Set: `Default Actions`
   - Click **Record**
4. **Image > Variables > Data Sets > Import**
   - Select: `c:\git\subscriber-list\data\levels.csv`
   - Click OK
5. **File > Export > Save for Web (Legacy)**
   - Format: JPEG, Quality: 80
   - Save to: `C:\Users\dusosl\Dropbox\Youtube\Patreon6.jpg`
6. Click **Stop Recording** (square button)

### Daily Usage

#### Full Automation (Recommended)

Double-click: **`scripts/update_patreon_image.bat`**

Or run:
```bash
python scripts/update_patreon_image.py
```

This will:
1. ✓ Fetch latest data from all platforms
2. ✓ Generate `data/levels.csv`
3. ✓ Open Photoshop with your PSD
4. ✓ Run the action to import data and export JPG
5. ✓ Complete in ~60 seconds

#### Data Generation Only

```bash
python src/subtext.py
```

Then manually run the Photoshop action.

#### Photoshop Update Only

If you already have fresh `data/levels.csv`:

```bash
python scripts/update_photoshop.py
```

### Taskbar Shortcut

For one-click access, pin to taskbar:

1. Double-click `scripts/UpdatePatreon.vbs` (creates desktop shortcut)
2. Right-click the desktop shortcut
3. Select **Pin to taskbar**

### Configuration

Edit paths in `scripts/update_photoshop.py` if needed:
- `PSD_PATH`: Your PSD file location
- `CSV_PATH`: Generated CSV location (default: `data/levels.csv`)
- `OUTPUT_PATH`: Where to save the JPG

Edit `scripts/trigger_action.jsx` to change:
- `actionName`: Photoshop action name (default: "UpdatePatreon")
- `actionSet`: Action set name (default: "Default Actions")

## Troubleshooting

### Photoshop Action Not Found

- Ensure action is named exactly: `UpdatePatreon`
- Verify it's in the "Default Actions" set
- Check action is not disabled (should have checkmark)

### Data Not Updating in Photoshop

- Verify `data/levels.csv` has recent timestamp
- Check PSD has variables configured (Image > Variables > Define)
- Ensure variable names match CSV column headers exactly (case-sensitive)

### Script Can't Find Photoshop

- Check Photoshop installation path in `scripts/update_photoshop.py`
- Add your Photoshop path to `PHOTOSHOP_PATHS` list if needed

### API Authentication Issues

- Delete token files (`.twitch_token.json`, etc.) and re-authenticate
- Verify API credentials in `.env` file
- Check redirect URIs match in both `.env` and API console

### Export Quality Issues

- Edit the Photoshop action and adjust JPEG quality setting
- Or manually set quality in Save for Web dialog when recording action

## License

This project is for personal use.
