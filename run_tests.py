import unittest
import multiprocessing
from unittest.runner import TextTestRunner
from unittest.loader import TestLoader

def run_test_suite(test_file):
    loader = TestLoader()
    suite = loader.discover(start_dir='.', pattern=test_file)
    runner = TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == '__main__':
    test_files = [
        'test_db_connections.py',
        'test_transactions.py',
        'test_data_validation.py'
    ]
    
    processes = []
    for test_file in test_files:
        process = multiprocessing.Process(target=run_test_suite, args=(test_file,))
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()