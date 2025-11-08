# Photoshop Action Setup Guide

## Quick Setup (5 minutes)

### Step 1: Create the Action

1. **Open Photoshop**

2. **Window > Actions** (or press Alt+F9)

3. **Create New Action:**
   - Click the folder icon at bottom (or click menu > New Action)
   - Name: `UpdatePatreon`
   - Set: `Default Actions`
   - Click **Record** button

4. **Record Step 1 - Import Data:**
   - **Image > Variables > Data Sets...**
   - Click **Import...**
   - Browse to: `c:\git\subscriber-list\levels.csv`
   - Click **OK** to import
   - Click **OK** to close dialog

5. **Record Step 2 - Export JPG:**
   - **File > Export > Save for Web (Legacy)...**
   - Settings:
     - Format: **JPEG**
     - Quality: **80** (or your preference)
   - Click **Save**
   - Save to: `C:\Users\dusosl\Dropbox\Youtube\Patreon6.jpg`
   - Click **Save**

6. **Stop Recording:**
   - Click the stop button (square icon) in Actions panel

7. **Done!** Your action is ready.

### Step 2: Test the Action

1. Close the PSD (don't save)
2. Reopen `Patreon6.psd`
3. In Actions panel, select "UpdatePatreon"
4. Click the play button (triangle icon)
5. Verify the JPG was exported

### Step 3: Run the Automation

Now you can use the Python script:

```bash
python update_patreon_image.py
```

Or just the Photoshop part:

```bash
python update_photoshop.py
```

## Troubleshooting

### "Action not found" error

- Make sure the action is named exactly: `UpdatePatreon`
- Make sure it's in the "Default Actions" set
- Try editing `trigger_action.jsx` if you used a different name/set

### Action doesn't record steps

Some operations can't be recorded automatically. Use **Insert Menu Item**:
- Click Actions menu (≡) > Insert Menu Item
- Click the menu command you want
- Click OK

### File paths are wrong

Edit the action:
- Expand the "UpdatePatreon" action in the Actions panel
- Double-click a step to edit it
- Update the file paths

### Want to use a keyboard shortcut?

1. Double-click the action name
2. In the dialog, assign a Function Key (F2-F12)
3. Click OK

Now you can press that key to run the action instantly!

## Alternative: Manual Trigger

If the Python script doesn't work, you can still automate most of the process:

1. Run: `python subtext.py` (generates levels.csv)
2. Open `Patreon6.psd` in Photoshop
3. Press F2 (or your assigned key) to run the action
4. Done!

## Tips

- **Keep Photoshop open** between updates for faster processing
- **Assign F2 key** to the action for one-button execution
- **Test with a copy** of your PSD first to make sure it works
- **Save the action set** (Actions menu > Save Actions) as a backup

## What the Action Does

The action automates:
1. ✓ Importing CSV data into variables
2. ✓ Exporting as optimized JPG

You still need to:
- Generate the CSV (automated via Python)
- Open the PSD (automated via Python script)
- Trigger the action (automated via Python script)

With the action set up, the entire workflow is automated!
