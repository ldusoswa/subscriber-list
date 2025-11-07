# YouTube Auto-Fetch Feature

## Quick Start

You now have two options for getting YouTube member data:

### Option 1: Manual Download (Current - No Setup Required)
1. Go to YouTube Studio → Memberships
2. Download CSV
3. Run `python subtext.py`

### Option 2: Automatic Fetch (Requires Setup)
1. Follow the setup guide in `YOUTUBE_API_SETUP.md`
2. Change `auto_fetch_youtube: bool = False` to `True` in `subtext.py`
3. Run `python subtext.py` - it will automatically fetch your members!

## What's New

### Files Added:
- **`youtube_api.py`** - Handles YouTube Data API integration
- **`YOUTUBE_API_SETUP.md`** - Complete setup instructions
- **`.gitignore`** - Updated to protect your API credentials

### Code Changes:
- Added `auto_fetch_youtube` config option in `subtext.py`
- New `fetch_youtube_members()` method that runs before processing
- Automatically saves fetched data in YouTube's CSV format

## Benefits of Auto-Fetch

✅ **No manual downloads** - Script fetches data automatically  
✅ **Always up-to-date** - Gets latest members every time you run it  
✅ **Same format** - Saves in YouTube's CSV format, works with existing code  
✅ **Optional** - Keep using manual downloads if you prefer  

## Important Notes

⚠️ **YouTube Members API requires approval** - You need to apply for access  
⚠️ **Setup takes ~30 minutes** - But only needs to be done once  
⚠️ **Credentials are private** - Never share your `youtube_credentials.json`  

## Testing Without API Access

You can test the integration without API approval:
```python
# In subtext.py, temporarily set:
auto_fetch_youtube: bool = True
```

Run it - you'll see it attempt to fetch, then fall back to using your existing CSV files.

## Need Help?

See `YOUTUBE_API_SETUP.md` for detailed setup instructions and troubleshooting.
