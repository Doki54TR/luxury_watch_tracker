"""
This script serves as the Automation Manager for the Price Tracker project.

It utilizes the `schedule` library to execute the data collection (scraper.py) 
and analysis (tracker.py) scripts automatically at defined intervals. 

Key Features:
- Orchestrates the workflow: Runs Scraper first, then Tracker.
- Error Handling: Prevents the tracker from running if the scraper encounters an error.
- Scheduling: Configured to run daily tasks at specific times (e.g., 09:00 and 21:00).
"""

import schedule
import time
import subprocess
import os
import sys

# --- CONFIGURATION ---
PYTHON_EXECUTABLE = sys.executable  # Uses the current python path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_job():
    print("\n⏰ Time to work! Starting the automation sequence...")
    
    # 1. Run the Scraper (Data Collection)
    print("--------------------------------------------------")
    print("🚀 Step 1: Running Scraper...")
    try:
        # We use subprocess to run the script just like running it in terminal
        result = subprocess.run([PYTHON_EXECUTABLE, "scraper.py"], cwd=PROJECT_DIR)
        
        if result.returncode == 0:
            print("✅ Scraper finished successfully.")
        else:
            print("❌ Scraper failed. Skipping tracker.")
            return # Stop if scraper fails
    except Exception as e:
        print(f"❌ Error executing scraper: {e}")
        return

    # 2. Run the Tracker (Analysis & Notification)
    print("--------------------------------------------------")
    print("🚀 Step 2: Running Price Tracker...")
    try:
        subprocess.run([PYTHON_EXECUTABLE, "tracker.py"], cwd=PROJECT_DIR)
        print("✅ Tracker finished.")
    except Exception as e:
        print(f"❌ Error executing tracker: {e}")
    
    print("--------------------------------------------------")
    print("💤 Job done. Waiting for the next schedule...\n")

# --- SCHEDULING ---

# OPTION A: For Testing (Runs every 2 minutes)
#schedule.every(2).minutes.do(run_job)

# OPTION B: Real Usage (Runs every day at specific times)
#schedule.every().day.at("09:00").do(run_job)
#schedule.every().day.at("21:00").do(run_job)

# OPTION C: Every 6 hours (4 times a day)
print("⏳ Schedule set: Running every 6 hours...")
schedule.every(6).hours.do(run_job)

print("🤖 Automation Bot is Online!")
# print("⏳ Waiting for the schedule trigger (Every 2 minutes)...") # Updated log message


# First run immediately to show it works? (Optional)
# run_job() 

# Infinite Loop to keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)