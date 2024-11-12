import unittest
import sqlite3
from recommendations import get_book_recommendations

class TestTDD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up an in-memory SQLite database
        cls.conn = sqlite3.connect(":memory:")
        cls.conn.row_factory = sqlite3.Row  # to access rows by column name
        cls.cursor = cls.conn.cursor()

        # Create tables
        cls.cursor.execute("""
            CREATE TABLE authors (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        cls.cursor.execute("""
            CREATE TABLE genres (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        cls.cursor.execute("""
            CREATE TABLE books (
                id INTEGER PRIMARY KEY,
                title TEXT,
                description TEXT,
                author_id INTEGER,
                genre_id INTEGER,
                FOREIGN KEY(author_id) REFERENCES authors(id),
                FOREIGN KEY(genre_id) REFERENCES genres(id)
            )
        """)

        # Insert sample data
        cls.cursor.execute("INSERT INTO authors (name) VALUES ('Test Author 1'), ('Test Author 2')")
        cls.cursor.execute("INSERT INTO genres (name) VALUES ('Fantasy'), ('Science Fiction')")
        cls.cursor.execute("""
            INSERT INTO books (title, description, author_id, genre_id)
            VALUES ('Test Book 1', 'Description 1', 1, 1),
                   ('Test Book 2', 'Description 2', 2, 2)
        """)
        cls.conn.commit()

    @classmethod
    def tearDownClass(cls):
        # Close the database connection
        cls.conn.close()

    def test_get_book_recommendations(self):
        """Test book recommendations with actual database and query"""
        preferences = {
            "genres": ["Fantasy"],
            "authors": ["Test Author 1"],
            "max_results": 5
        }

        # Define a replacement for the `get_db_connection` function
        def mock_get_db_connection():
            return self.conn

        # Patch the `get_db_connection` function in `recommendations` to use our in-memory DB
        with patch('recommendations.get_db_connection', mock_get_db_connection):
            # Call the recommendation function
            recommendations = get_book_recommendations(preferences)
        
        # Assertions
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), preferences["max_results"])
        
        # Check content of recommendations to ensure query correctness
        self.assertEqual(recommendations[0]['title'], 'Test Book 1')
        self.assertEqual(recommendations[0]['author'], 'Test Author 1')
        self.assertEqual(recommendations[0]['genre'], 'Fantasy')

# Run the tests
if __name__ == '__main__':
    unittest.main()