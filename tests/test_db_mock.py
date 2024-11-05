import unittest
from unittest.mock import Mock, patch
from tests.utils import BookshopTestRunner, setup_mock_data
from models import BookCreate

class TestDatabaseMock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        runner = BookshopTestRunner()
        cls.args = runner.parser.parse_args()
        if cls.args.mock_data:
            cls.mock_data = setup_mock_data()

    def setUp(self):
        self.db_mock = Mock()
        self.cursor_mock = Mock()
        self.db_mock.cursor.return_value = self.cursor_mock

    @patch('crud.get_db_connection')
    def test_create_book(self, mock_db_conn):
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
        self.assertNotEqual(result["description"], "Wrong Test Description")
        self.assertGreater(result["author_id"], 0)
        self.assertLess(result["genre_id"], 2)
        self.cursor_mock.execute.assert_called_once()
        
        if self.args.verbose:
            print(f"\nTest create_book result: {result}")
