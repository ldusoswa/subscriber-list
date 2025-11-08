# Quick Start Guide - Photoshop Automation

## ✅ One-Time Setup (5 minutes)

### Step 1: Create Photoshop Action

1. Open Photoshop
2. Press **Alt+F9** (or Window > Actions)
3. Click **New Action** button (folder icon)
   - Name: `UpdatePatreon`
   - Click **Record**
4. **Image > Variables > Data Sets > Import**
   - Select: `c:\git\subscriber-list\levels.csv`
   - Click OK
5. **File > Export > Save for Web (Legacy)**
   - Format: JPEG, Quality: 80
   - Save to: `C:\Users\dusosl\Dropbox\Youtube\Patreon6.jpg`
6. Click **Stop** (square button)

**Done!** Action created.

### Step 2: Test It

1. Close the PSD
2. Reopen `Patreon6.psd`
3. Select "UpdatePatreon" action
4. Click Play button (triangle)
5. Verify JPG was created

## 🚀 Daily Usage

### Full Automation (Recommended)

Double-click: **`update_patreon_image.bat`**

Or run:
```bash
python update_patreon_image.py
```

This will:
1. ✓ Fetch latest subscriber data from APIs
2. ✓ Generate levels.csv
3. ✓ Open Photoshop with your PSD
4. ✓ Run the action to import data and export JPG
5. ✓ Done!

**Total time: ~60 seconds** (mostly automated)

### Update Data Only

If you just want to generate fresh data:

```bash
python subtext.py
```

Then manually run the action in Photoshop.

## 💡 Pro Tips

### Assign Keyboard Shortcut

1. Double-click "UpdatePatreon" action name
2. Assign Function Key: **F2**
3. Click OK

Now: Generate data → Open PSD → Press **F2** → Done!

### Keep Photoshop Open

Leave Photoshop running between updates for faster processing.

### Automate Data Generation

Use Windows Task Scheduler to run `subtext.py` daily at a specific time.

## 📁 Files You Need

- ✓ `update_patreon_image.py` - Full automation script
- ✓ `update_patreon_image.bat` - Easy launcher
- ✓ `update_photoshop.py` - Photoshop-only automation
- ✓ `trigger_action.jsx` - JSX script that triggers the action
- ✓ `subtext.py` - Data generation script

## ❓ Troubleshooting

### "Action not found" error
- Make sure action is named exactly: `UpdatePatreon`
- Make sure it's in "Default Actions" set

### Script doesn't launch Photoshop
- Check Photoshop installation path in `update_photoshop.py`
- Try running Photoshop manually first

### Data not updating
- Verify `levels.csv` has recent timestamp
- Check that PSD has variables configured
- See `PHOTOSHOP_SETUP.md` for variable setup

### Export quality issues
- Edit the action and change JPEG quality setting
- Or manually adjust in Save for Web dialog

## 📚 More Help

- **Action Setup**: See `ACTION_SETUP_GUIDE.md`
- **Variable Setup**: See `PHOTOSHOP_SETUP.md`
- **API Setup**: See main `README.md`

## ✨ Success!

Once set up, you have a nearly-fully-automated workflow:
- Data fetching: **100% automated**
- Photoshop update: **100% automated** (with action)
- Total manual time: **~5 seconds** (just run the batch file!)

Enjoy your automated Patreon image updates! 🎉
