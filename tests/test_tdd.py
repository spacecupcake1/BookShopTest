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
        
        # Mock the cursor's dictionary-like behavior
        self.cursor_mock.fetchall.return_value = [{
            'id': 1,
            'title': 'Test Book 1',
            'description': 'Description 1',
            'author': 'Test Author 1',
            'genre': 'Fantasy'
        }]

    def validate_sql_syntax(self, sql_query, params):
        """Helper method to validate SQL syntax using a temporary SQLite connection"""
        try:
            # Create a temporary SQLite connection to verify SQL syntax
            temp_conn = sqlite3.connect(':memory:')
            cursor = temp_conn.cursor()
            
            # Create temporary tables matching our schema
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
            
            # Try to prepare the query (this will catch syntax errors)
            cursor.execute("EXPLAIN QUERY PLAN " + sql_query, params)
            return True
            
        except sqlite3.Error as e:
            return False
            
        finally:
            temp_conn.close()

    def test_get_book_recommendations(self):
        """Test book recommendations system with database mocking"""
        # Test data
        preferences = {
            "genres": ["Fantasy", "Science Fiction"],
            "authors": ["Test Author 1", "Test Author 2"],
            "max_results": 5
        }
        
        # Set up the database connection mock
        with patch('recommendations.get_db_connection') as mock_db_conn:
            mock_db_conn.return_value.__enter__.return_value = self.db_mock
            
            # Get recommendations
            from recommendations import get_book_recommendations
            recommendations = get_book_recommendations(preferences)
            
            # Get the actual query and parameters
            actual_query = self.cursor_mock.execute.call_args[0][0].strip()
            actual_params = self.cursor_mock.execute.call_args[0][1]
            
            # Validate SQL syntax
            is_valid_sql = self.validate_sql_syntax(actual_query, actual_params)
            self.assertTrue(is_valid_sql, "Invalid SQL syntax in query")
            
            # Verify specific parts of the query
            expected_parts = [
                "SELECT DISTINCT",
                "b.id",
                "b.title",
                "b.description",
                "a.name as author",
                "g.name as genre",
                "FROM books b",
                "JOIN authors a ON b.author_id = a.id",
                "JOIN genres g ON b.genre_id = g.id",
                "WHERE"
            ]
            
            for part in expected_parts:
                self.assertIn(part, actual_query, f"Missing or incorrect part in query: {part}")
            
            # Verify the cursor was created
            self.db_mock.cursor.assert_called_once()
            
            # Verify the query parameters
            expected_params = ['Fantasy', 'Science Fiction', 'Test Author 1', 'Test Author 2', 5]
            self.assertEqual(actual_params, expected_params)
            
            # Verify the results
            self.assertIsInstance(recommendations, list)
            self.assertLessEqual(len(recommendations), preferences["max_results"])
            
            # Verify the structure of returned recommendations
            for recommendation in recommendations:
                self.assertIn('id', recommendation)
                self.assertIn('title', recommendation)
                self.assertIn('description', recommendation)
                self.assertIn('author', recommendation)
                self.assertIn('genre', recommendation)
            
            if self.args.verbose:
                print(f"\nTest recommendations: {recommendations}")
                print(f"\nActual SQL query: {actual_query}")
                print(f"\nQuery parameters: {actual_params}")

    def test_get_book_recommendations_empty_preferences(self):
        """Test recommendations with empty preferences"""
        preferences = {
            "genres": [],
            "authors": [],
            "max_results": 5
        }
        
        with patch('recommendations.get_db_connection') as mock_db_conn:
            mock_db_conn.return_value.__enter__.return_value = self.db_mock
            
            from recommendations import get_book_recommendations
            recommendations = get_book_recommendations(preferences)
            
            # Verify empty list is returned for empty preferences
            self.assertEqual(recommendations, [])
            
            # Verify that no database query was executed
            self.cursor_mock.execute.assert_not_called()

    def test_get_book_recommendations_genres_only(self):
        """Test recommendations with only genre preferences"""
        preferences = {
            "genres": ["Fantasy"],
            "authors": [],
            "max_results": 5
        }
        
        with patch('recommendations.get_db_connection') as mock_db_conn:
            mock_db_conn.return_value.__enter__.return_value = self.db_mock
            
            from recommendations import get_book_recommendations
            recommendations = get_book_recommendations(preferences)
            
            # Get the actual query and parameters
            actual_query = self.cursor_mock.execute.call_args[0][0].strip()
            actual_params = self.cursor_mock.execute.call_args[0][1]
            
            # Validate SQL syntax
            is_valid_sql = self.validate_sql_syntax(actual_query, actual_params)
            self.assertTrue(is_valid_sql, "Invalid SQL syntax in query")
            
            # Verify the query only includes genre condition
            self.assertIn("g.name IN (?)", actual_query)
            self.assertNotIn("a.name IN", actual_query)
            
            # Verify parameters
            self.assertEqual(actual_params, ['Fantasy', 5])