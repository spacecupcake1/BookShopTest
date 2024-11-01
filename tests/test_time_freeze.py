import unittest
import freezegun
from datetime import datetime
from tests.utils import BookshopTestRunner

class TestTimeFreeze(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        runner = BookshopTestRunner()
        cls.args = runner.parser.parse_args()
        
        if cls.args.time_freeze:
            cls.freeze_time = freezegun.freeze_time(cls.args.time_freeze)
            cls.freeze_time.start()
    
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'freeze_time'):
            cls.freeze_time.stop()

    @freezegun.freeze_time("2024-01-01")
    def test_book_timestamp(self):
        """Test book creation timestamp with frozen time if specified"""
        if self.args.test_type == 'time-freeze':
            current_time = datetime.now()
            self.assertEqual(current_time.year, 2024)
            self.assertEqual(current_time.month, 1)
            self.assertEqual(current_time.day, 1)
            
            if self.args.verbose:
                print(f"\nTest timestamp: {current_time}")