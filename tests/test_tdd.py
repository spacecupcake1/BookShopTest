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
        # Create mock database connection and cursor
        self.db_mock = Mock()
        self.cursor_mock = Mock()
        self.db_mock.cursor.return_value = self.cursor_mock
        
        # Define mock database row structure
        self.mock_db_row = {
            'id': 1,
            'title': 'Test Book 1',
            'description': 'Description 1',
            'author': 'Test Author 1',
            'genre': 'Fantasy'
        }
        
        # Mock cursor to return row-like objects
        self.cursor_mock.fetchall.return_value = [self.mock_db_row]

    def validate_sql_syntax(self, sql_query, params):
        """Helper method to validate SQL syntax"""
        try:
            temp_conn = sqlite3.connect(':memory:')
            cursor = temp_conn.cursor()
            
            # Create test schema
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
        """Helper method to validate the structure and data types of a recommendation"""
        required_fields = {
            'id': int,
            'title': str,
            'description': str,
            'author': str,
            'genre': str
        }
        
        for field, expected_type in required_fields.items():
            if field not in recommendation:
                return False
            if not isinstance(recommendation[field], expected_type):
                return False
        return True

    def test_field_mapping(self):
        """Test correct field mapping from database to recommendation object"""
        preferences = {
            "genres": ["Fantasy"],
            "authors": ["Test Author 1"],
            "max_results": 5
        }
        
        test_db_row = {
            'id': 42,
            'title': 'Specific Test Title',
            'description': 'Specific Test Description',
            'author': 'Specific Test Author',
            'genre': 'Specific Test Genre'
        }
        
        self.cursor_mock.fetchall.return_value = [test_db_row]
        
        with patch('recommendations.get_db_connection') as mock_db_conn:
            mock_db_conn.return_value.__enter__.return_value = self.db_mock
            
            from recommendations import get_book_recommendations
            recommendations = get_book_recommendations(preferences)
            
            self.assertEqual(len(recommendations), 1)
            recommendation = recommendations[0]
            
            # Verify exact field mappings and types
            for field in test_db_row:
                self.assertEqual(recommendation[field], test_db_row[field])
                self.assertEqual(type(recommendation[field]), type(test_db_row[field]))

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
            
            # Verify query syntax and structure
            actual_query = self.cursor_mock.execute.call_args[0][0].strip()
            actual_params = self.cursor_mock.execute.call_args[0][1]
            is_valid_sql = self.validate_sql_syntax(actual_query, actual_params)
            self.assertTrue(is_valid_sql, "Invalid SQL syntax in query")
            
            # Verify recommendations structure and content
            self.assertIsInstance(recommendations, list)
            self.assertLessEqual(len(recommendations), preferences["max_results"])
            for recommendation in recommendations:
                self.assertTrue(
                    self.validate_recommendation_structure(recommendation),
                    f"Invalid recommendation structure: {recommendation}"
                )

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
                
                # Adjust mock return value based on max_results
                if case["max_results"] <= 0:
                    self.cursor_mock.fetchall.return_value = []
                elif case["max_results"] == 1:
                    self.cursor_mock.fetchall.return_value = [self.mock_db_row]
                else:
                    self.cursor_mock.fetchall.return_value = [self.mock_db_row] * min(case["max_results"], 2)
                
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

    def test_invalid_preference_format(self):
        """Test handling of invalid preference formats"""
        invalid_cases = [
            {
                "preferences": {"genres": None, "authors": [], "max_results": 5},
                "expected_error": TypeError
            },
            {
                "preferences": {"genres": ["Fantasy"], "authors": "Invalid", "max_results": 5},
                "expected_error": TypeError
            },
            {
                "preferences": {"genres": [], "authors": [], "max_results": "5"},
                "expected_error": TypeError
            }
        ]
        
        for case in invalid_cases:
            with self.assertRaises(case["expected_error"]):
                from recommendations import get_book_recommendations
                recommendations = get_book_recommendations(case["preferences"])

    def test_database_connection_error(self):
        """Test handling of database connection errors"""
        preferences = {
            "genres": ["Fantasy"],
            "authors": [],
            "max_results": 5
        }
        
        with patch('recommendations.get_db_connection') as mock_db_conn:
            mock_db_conn.side_effect = sqlite3.Error("Connection failed")
            
            from recommendations import get_book_recommendations
            with self.assertRaises(Exception) as context:
                recommendations = get_book_recommendations(preferences)
            
            self.assertIn("Database error", str(context.exception))

    def test_sql_injection_prevention(self):
        """Test prevention of SQL injection attempts"""
        malicious_preferences = {
            "genres": ["Fantasy'; DROP TABLE books; --"],
            "authors": ["Robert'; DELETE FROM authors; --"],
            "max_results": 5
        }
        
        with patch('recommendations.get_db_connection') as mock_db_conn:
            mock_db_conn.return_value.__enter__.return_value = self.db_mock
            
            from recommendations import get_book_recommendations
            recommendations = get_book_recommendations(malicious_preferences)
            
            # Check query parameterization
            actual_query = self.cursor_mock.execute.call_args[0][0]
            actual_params = self.cursor_mock.execute.call_args[0][1]
            
            # Verify no raw SQL in query
            self.assertNotIn("DROP TABLE", actual_query)
            self.assertNotIn("DELETE FROM", actual_query)
            self.assertIn("?", actual_query)
            
            # Verify parameters are passed separately
            self.assertEqual(actual_params[0], "Fantasy'; DROP TABLE books; --")
            
            # Verify recommendations are still valid
            self.assertIsInstance(recommendations, list)
            for recommendation in recommendations:
                self.assertTrue(
                    self.validate_recommendation_structure(recommendation),
                    f"Invalid recommendation structure: {recommendation}"
                )