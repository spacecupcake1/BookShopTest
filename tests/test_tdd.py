import unittest
from unittest.mock import Mock, patch
from tests.utils import BookshopTestRunner
import sqlite3

class TestTDD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        runner = BookshopTestRunner()
        cls.args = runner.parser.parse_args()

    def setUp(self):
        self.db_mock = Mock()
        self.cursor_mock = Mock()
        self.db_mock.cursor.return_value = self.cursor_mock
        
        # Define test data that will be returned by the mock
        self.test_recommendations = [{
            'id': 1,
            'title': 'Test Book 1',
            'description': 'Description 1',
            'author': 'Test Author 1',
            'genre': 'Fantasy'
        }, {
            'id': 2,
            'title': 'Test Book 2',
            'description': 'Description 2',
            'author': 'Test Author 1',
            'genre': 'Science Fiction'
        }]
        
        # Default mock behavior
        self.cursor_mock.fetchall.return_value = self.test_recommendations

    def validate_sql_syntax(self, sql_query, params):
        """Helper method to validate SQL syntax using a temporary SQLite connection"""
        try:
            temp_conn = sqlite3.connect(':memory:')
            cursor = temp_conn.cursor()
            
            cursor.execute("""
                CREATE TABLE authors (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE genres (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE books (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    author_id INTEGER,
                    genre_id INTEGER,
                    FOREIGN KEY (author_id) REFERENCES authors (id),
                    FOREIGN KEY (genre_id) REFERENCES genres (id)
                )
            """)
            
            cursor.execute("EXPLAIN QUERY PLAN " + sql_query, params)
            return True
            
        except sqlite3.Error as e:
            print(f"SQL Error: {str(e)}")
            return False
            
        finally:
            temp_conn.close()

    def test_data_equality_in_recommendations(self):
        # Define preferences for the test
        preferences = {
            "genres": ["Fantasy"],
            "authors": ["Test Author 1"],
            "max_results": 5
        }

        # Define the expected data
        expected_data = [
            {
                "id": 1,
                "title": "Test Book 1",
                "description": "Description 1",
                "author": "Test Author 1",
                "genre": "Fantasy"
            }
        ]

    def validate_recommendation_structure(self, recommendation):
        """Helper method to validate the structure of a recommendation"""
        required_fields = ['id', 'title', 'description', 'author', 'genre']
        for field in required_fields:
            if field not in recommendation:
                return False
            if not isinstance(recommendation[field], (str, int)):
                return False
        return True

    def test_max_results_boundary(self):
        """Test boundary conditions for max_results"""
        test_cases = [
            {"max_results": 0},
            {"max_results": -1},
            {"max_results": 1},
            {"max_results": 100}
        ]
        
        for case in test_cases:
            preferences = {
                "genres": ["Fantasy"],
                "authors": [],
                **case
            }
            
            with patch('recommendations.get_db_connection') as mock_db_conn:
                mock_db_conn.return_value.__enter__.return_value = self.db_mock
                
                # Dynamically adjust mock return value based on max_results
                if case["max_results"] <= 0:
                    self.cursor_mock.fetchall.return_value = []
                elif case["max_results"] == 1:
                    self.cursor_mock.fetchall.return_value = self.test_recommendations[:1]
                else:
                    self.cursor_mock.fetchall.return_value = self.test_recommendations
                
                from recommendations import get_book_recommendations
                recommendations = get_book_recommendations(preferences)
                
                if case["max_results"] <= 0:
                    self.assertEqual(recommendations, [])
                else:
                    self.assertLessEqual(len(recommendations), case["max_results"])
                    for recommendation in recommendations:
                        self.assertTrue(
                            self.validate_recommendation_structure(recommendation),
                            f"Invalid recommendation structure: {recommendation}"
                        )
                    
                    # Verify the LIMIT clause in the query
                    actual_query = self.cursor_mock.execute.call_args[0][0].strip()
                    self.assertIn("LIMIT ?", actual_query)
                    actual_params = self.cursor_mock.execute.call_args[0][1]
                    self.assertEqual(actual_params[-1], case["max_results"])

    def test_empty_preferences(self):
        """Test handling of empty preferences"""
        preferences = {
            "genres": [],
            "authors": [],
            "max_results": 5
        }
        
        with patch('recommendations.get_db_connection') as mock_db_conn:
            mock_db_conn.return_value.__enter__.return_value = self.db_mock
            
            from recommendations import get_book_recommendations
            recommendations = get_book_recommendations(preferences)
            
            self.assertEqual(recommendations, [])
            self.cursor_mock.execute.assert_not_called()

    def test_get_book_recommendations_basic(self):
        """Test basic book recommendations functionality"""
        preferences = {
            "genres": ["Fantasy"],
            "authors": ["Test Author 1"],
            "max_results": 5
        }
        
        with patch('recommendations.get_db_connection') as mock_db_conn:
            mock_db_conn.return_value.__enter__.return_value = self.db_mock
            
            from recommendations import get_book_recommendations
            recommendations = get_book_recommendations(preferences)
            
            actual_query = self.cursor_mock.execute.call_args[0][0].strip()
            actual_params = self.cursor_mock.execute.call_args[0][1]
            is_valid_sql = self.validate_sql_syntax(actual_query, actual_params)
            self.assertTrue(is_valid_sql, "Invalid SQL syntax in query")
            
            self.assertIsInstance(recommendations, list)
            self.assertLessEqual(len(recommendations), preferences["max_results"])
            for recommendation in recommendations:
                self.assertTrue(
                    self.validate_recommendation_structure(recommendation),
                    f"Invalid recommendation structure: {recommendation}"
                )
