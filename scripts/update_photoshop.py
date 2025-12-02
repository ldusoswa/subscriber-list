"""
Automates updating Photoshop PSD file by triggering a Photoshop action.

This script:
1. Opens Photoshop with the PSD file
2. Triggers a Photoshop action named "UpdatePatreon"

Prerequisites:
- Create a Photoshop action named "UpdatePatreon" in "Default Actions" that:
  1. Imports data: Image > Variables > Data Sets > Import > levels.csv
  2. Exports JPG: File > Export > Save for Web > Patreon8.jpg
"""

import os
import sys
import subprocess
import time

# Configuration
PSD_PATH = r"C:\Users\dusosl\Dropbox\Youtube\Patreon8.psd"
CSV_PATH = r"c:\git\subscriber-list\data\levels.csv"
OUTPUT_PATH = r"C:\Users\dusosl\Dropbox\Youtube\Patreon8.jpg"
JSX_SCRIPT = r"c:\git\subscriber-list\scripts\trigger_action.jsx"

# Common Photoshop installation paths
PHOTOSHOP_PATHS = [
    r"C:\Program Files\Adobe\Adobe Photoshop 2026\Photoshop.exe",
    r"C:\Program Files\Adobe\Adobe Photoshop 2025\Photoshop.exe",
    r"C:\Program Files\Adobe\Adobe Photoshop 2024\Photoshop.exe",
    r"C:\Program Files\Adobe\Adobe Photoshop 2023\Photoshop.exe",
    r"C:\Program Files\Adobe\Adobe Photoshop 2022\Photoshop.exe",
    r"C:\Program Files\Adobe\Adobe Photoshop 2021\Photoshop.exe",
]


def find_photoshop():
    """Find Photoshop installation."""
    print("Searching for Photoshop...")
    for path in PHOTOSHOP_PATHS:
        if os.path.exists(path):
            print(f"✓ Found: {path}")
            return path
    print("✗ Photoshop not found in common locations")
    return None


def main():
    """Main workflow."""
    print("=" * 60)
    print("Photoshop Automation - Action Trigger Method")
    print("=" * 60)
    print()
    
    # Verify CSV exists
    if not os.path.exists(CSV_PATH):
        print(f"✗ Error: levels.csv not found at {CSV_PATH}")
        print("  Run subtext.py first to generate the CSV file.")
        sys.exit(1)
    
    print(f"✓ CSV file found: {CSV_PATH}")
    print(f"  Size: {os.path.getsize(CSV_PATH)} bytes")
    print()
    
    # Verify PSD exists
    if not os.path.exists(PSD_PATH):
        print(f"✗ Error: PSD file not found at {PSD_PATH}")
        sys.exit(1)
    
    print(f"✓ PSD file found: {PSD_PATH}")
    print()
    
    # Verify JSX script exists
    if not os.path.exists(JSX_SCRIPT):
        print(f"✗ Error: JSX script not found at {JSX_SCRIPT}")
        sys.exit(1)
    
    print(f"✓ JSX script found: {JSX_SCRIPT}")
    print()
    
    # Find Photoshop
    photoshop_exe = find_photoshop()
    if not photoshop_exe:
        print()
        print("Please install Photoshop or update PHOTOSHOP_PATHS in this script.")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("Launching Photoshop...")
    print("=" * 60)
    print()
    print("Photoshop will open and run the action.")
    print("Check Photoshop for any dialogs or errors.")
    print()
    
    try:
        # Launch Photoshop with the JSX script
        subprocess.Popen([photoshop_exe, JSX_SCRIPT])
        
        print("✓ Photoshop launched successfully")
        print()
        print("The script will:")
        print("1. Open Patreon8.psd")
        print("2. Run the 'UpdatePatreon' action")
        print("3. Show a completion dialog")
        print()
        print("Please check Photoshop for the result.")
        
        # Wait a bit to see if there are immediate errors
        time.sleep(3)
        
        # Check if output was created (may take a while)
        print()
        print("Waiting for export to complete...")
        for i in range(30):  # Wait up to 30 seconds
            if os.path.exists(OUTPUT_PATH):
                print()
                print("=" * 60)
                print("✓ SUCCESS!")
                print("=" * 60)
                print(f"Output: {OUTPUT_PATH}")
                print(f"Size: {os.path.getsize(OUTPUT_PATH):,} bytes")
                return
            time.sleep(1)
            print(".", end="", flush=True)
        
        print()
        print()
        print("⚠ Export file not detected yet.")
        print("  Check Photoshop to see if the action completed.")
        print("  The action may require manual confirmation.")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
