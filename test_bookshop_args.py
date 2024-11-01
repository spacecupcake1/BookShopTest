# test_bookshop_args.py
import unittest
import sys
import argparse
from unittest.mock import Mock, patch
from datetime import datetime
import freezegun
from models import BookCreate, AuthorCreate, GenreCreate

class BookshopTestRunner:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Run Bookshop Tests')
        self.setup_arguments()
        
    def setup_arguments(self):
        self.parser.add_argument(
            '--test-type',
            choices=['db-mock', 'time-freeze', 'tdd'],
            help='Type of test to run'
        )
        self.parser.add_argument(
            '--mock-data',
            action='store_true',
            help='Use mock data instead of test database'
        )
        self.parser.add_argument(
            '--time-freeze',
            type=str,
            help='Freeze time to specified datetime (format: YYYY-MM-DD)'
        )
        self.parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed test output'
        )

class TestBookshopWithArgs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Parse command line arguments
        runner = BookshopTestRunner()
        cls.args = runner.parser.parse_args()
        
        # Setup based on arguments
        if cls.args.mock_data:
            cls.setup_mock_data()
            
        if cls.args.time_freeze:
            cls.freeze_time = freezegun.freeze_time(cls.args.time_freeze)
            cls.freeze_time.start()
    
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'freeze_time'):
            cls.freeze_time.stop()
    
    @classmethod
    def setup_mock_data(cls):
        cls.mock_books = [
            BookCreate(
                title="Test Book 1",
                description="Description 1",
                author_id=1,
                genre_id=1
            ),
            BookCreate(
                title="Test Book 2",
                description="Description 2",
                author_id=2,
                genre_id=1
            )
        ]
        
        cls.mock_authors = [
            AuthorCreate(name="Test Author 1"),
            AuthorCreate(name="Test Author 2")
        ]
        
        cls.mock_genres = [
            GenreCreate(name="Fantasy"),
            GenreCreate(name="Science Fiction")
        ]

    def setUp(self):
        self.db_mock = Mock()
        self.cursor_mock = Mock()
        self.db_mock.cursor.return_value = self.cursor_mock

    @patch('crud.get_db_connection')
    def test_create_book(self, mock_db_conn):
        """Test creating a book with mock data if specified"""
        if self.args.test_type == 'db-mock':
            # Setup mock
            mock_db_conn.return_value.__enter__.return_value = self.db_mock
            self.cursor_mock.lastrowid = 1
            
            # Create test data using BookCreate model
            book_data = BookCreate(
                title="New Test Book",
                description="Test Description",
                author_id=1,
                genre_id=1
            )
            
            # Perform test
            from crud import create_book
            result = create_book(book_data)
            
            # Assertions
            self.assertEqual(result["id"], 1)
            self.assertEqual(result["title"], "New Test Book")
            self.cursor_mock.execute.assert_called_once()
            
            if self.args.verbose:
                print(f"\nTest create_book result: {result}")

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

    def test_get_book_recommendations(self):
        """Test book recommendations system (TDD approach)"""
        if self.args.test_type == 'tdd':
            # Test data
            preferences = {
                "genres": ["Fantasy"],
                "authors": ["Test Author 1"],
                "max_results": 5
            }
            
            # Mock the database response if using mock data
            if self.args.mock_data:
                mock_results = [
                    {
                        "id": 1,
                        "title": "Test Book 1",
                        "description": "Description 1",
                        "author": "Test Author 1",
                        "genre": "Fantasy"
                    }
                ]
                self.cursor_mock.fetchall.return_value = mock_results
            
            # Perform test
            from recommendations import get_book_recommendations
            with patch('recommendations.get_db_connection') as mock_db_conn:
                mock_db_conn.return_value.__enter__.return_value = self.db_mock
                recommendations = get_book_recommendations(preferences)
            
            # Assertions
            self.assertIsInstance(recommendations, list)
            self.assertLessEqual(len(recommendations), preferences["max_results"])
            
            if self.args.verbose:
                print(f"\nTest recommendations: {recommendations}")

def run_tests():
    # Create test suite based on command line arguments
    runner = BookshopTestRunner()
    args = runner.parser.parse_args()
    
    # Configure test output verbosity
    verbosity = 2 if args.verbose else 1
    
    # Run the tests
    unittest.main(argv=[sys.argv[0]], verbosity=verbosity)

if __name__ == '__main__':
    run_tests()