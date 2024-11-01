import unittest
from unittest.mock import Mock, patch
from tests.utils import BookshopTestRunner, setup_mock_data

class TestTDD(unittest.TestCase):
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