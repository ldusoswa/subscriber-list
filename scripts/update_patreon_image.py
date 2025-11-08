"""
Complete workflow: Fetch subscriber data and update Patreon Photoshop image.

This script runs the full automation:
1. Fetches data from YouTube, Twitch, and Patreon APIs
2. Generates levels.csv
3. Updates Photoshop PSD with new data
4. Exports as JPG
"""

import subprocess
import sys
import os
from pathlib import Path


def run_script(script_name, description):
    """Run a Python script and handle errors."""
    print()
    print("=" * 60)
    print(f"STEP: {description}")
    print("=" * 60)
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False,
            text=True
        )
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"✗ Script not found: {script_name}")
        return False


def main():
    """Run the complete workflow."""
    print("=" * 60)
    print("PATREON IMAGE UPDATE - FULL WORKFLOW")
    print("=" * 60)
    
    # Get the repository root directory
    repo_root = Path(__file__).parent.parent
    os.chdir(repo_root)
    
    # Step 1: Fetch subscriber data and generate levels.csv
    if not run_script("src/subtext.py", "Fetch subscriber data and generate levels.csv"):
        print()
        print("✗ Failed to generate levels.csv. Aborting.")
        sys.exit(1)
    
    # Step 2: Update Photoshop and export
    if not run_script("scripts/update_photoshop.py", "Update Photoshop PSD and export JPG"):
        print()
        print("✗ Failed to update Photoshop. Please check the errors above.")
        sys.exit(1)
    
    # Success!
    print()
    print("=" * 60)
    print("✓ COMPLETE WORKFLOW FINISHED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("Your Patreon6.jpg has been updated with the latest subscriber data.")


if __name__ == "__main__":
    main()
