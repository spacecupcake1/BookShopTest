import schedule
import time
import os
import subprocess

def run_tests():
    # Activate virtual environment and run pytest
    subprocess.call('source env/bin/activate && pytest', shell=True)

# Schedule the job every day at midnight
schedule.every().day.at("00:00").do(run_tests)

# Keep the script running to handle the scheduled jobs
while True:
    schedule.run_pending()
    time.sleep(60)
