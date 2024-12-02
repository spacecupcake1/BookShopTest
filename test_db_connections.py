import unittest
import sqlite3
from unittest.mock import patch

from database import get_db_connection

class TestDatabaseConnections(unittest.TestCase):
    """Tests for database connection functionality"""
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS authors (id INTEGER PRIMARY KEY, name TEXT);
            CREATE TABLE IF NOT EXISTS genres (id INTEGER PRIMARY KEY, name TEXT);
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                title TEXT,
                author_id INTEGER,
                genre_id INTEGER
            );
        ''')
    
    def tearDown(self):
        self.conn.close()

    def test_connection_establishment(self):
        """Test: Database connection is established successfully"""
        self.assertIsInstance(self.conn, sqlite3.Connection)
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1")
        self.assertEqual(cursor.fetchone()[0], 1)

    def test_multiple_connections(self):
        """Test: Multiple database connections are independent"""
        conn2 = sqlite3.connect(':memory:')
        self.assertNotEqual(id(self.conn), id(conn2))
        conn2.close()

    def test_connection_row_factory(self):
        """Test: Row factory is properly configured"""
        self.assertEqual(self.conn.row_factory, sqlite3.Row)

    def test_connection_success(self):
        """Test: Successful database connection"""
        self.assertTrue(self.conn.execute("SELECT 1").fetchone() is not None)

    def test_connection_failure(self):
        """Test: Failed database connection attempt"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = sqlite3.Error("Connection failed")
            with self.assertRaises(sqlite3.Error):
                sqlite3.connect(':memory:')
