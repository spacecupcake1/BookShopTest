import schedule
import time
import subprocess

def run_tests():
    # Activate virtual environment and run tests
    activate_command = r'env\Scripts\activate.bat'
    test_command = 'python -m tests.run_tests'
    
    # Run both commands in sequence
    subprocess.call(f'{activate_command} && {test_command}', shell=True)

# Schedule the job every day at 14:19
schedule.every().day.at("14:19").do(run_tests)

# Keep the script running to handle the scheduled jobs
while True:
    schedule.run_pending()
    time.sleep(60)
