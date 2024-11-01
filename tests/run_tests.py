import unittest
import sys
from tests.utils import BookshopTestRunner

def run_all_tests():
    # Create test suite based on command line arguments
    runner = BookshopTestRunner()
    args = runner.parser.parse_args()
    
    # Configure test output verbosity
    verbosity = 2 if args.verbose else 1
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = '.'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(suite)

if __name__ == '__main__':
    run_all_tests()