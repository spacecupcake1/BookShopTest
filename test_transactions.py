import unittest
from unittest.mock import patch
import sqlite3
from database import get_db_connection, init_db
from models import BookCreate, AuthorCreate, GenreCreate
from crud import create_book, create_author, create_genre
from test_base import BaseTest

class TestTransactions(unittest.TestCase):
    """Tests for transaction handling"""
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        self.conn.executescript('''
            CREATE TABLE authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );
            CREATE TABLE genres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
        ''')
    
    def tearDown(self):
        self.conn.close()

    def test_commit(self):
        """Test: Successful transaction commit"""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO authors (name) VALUES (?)", ("Test Author",))
        self.conn.commit()
        cursor.execute("SELECT name FROM authors")
        self.assertEqual(cursor.fetchone()['name'], "Test Author")

    def test_rollback(self):
        """Test: Transaction rollback functionality"""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO authors (name) VALUES (?)", ("Author 1",))
        self.conn.rollback()
        cursor.execute("SELECT COUNT(*) FROM authors")
        self.assertEqual(cursor.fetchone()[0], 0)

    def test_complex_transaction(self):
        """Test: Complex transaction with savepoints"""
        cursor = self.conn.cursor()
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute("SAVEPOINT sp1")

        cursor.execute("INSERT INTO authors (name) VALUES (?)", ("Author 1",))
        cursor.execute("ROLLBACK TO sp1")

        cursor.execute("SELECT COUNT(*) FROM authors")
        self.assertEqual(cursor.fetchone()[0], 0)

    def test_database_failure(self):
        """Test: Unexpected database failure during transaction"""
        cursor = self.conn.cursor()
        
        # Set journal mode to DELETE to force immediate writes
        cursor.execute("PRAGMA journal_mode = DELETE")
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute("INSERT INTO authors (name) VALUES (?)", ("Test Author",))
        
        # Force a failure by making the database read-only
        cursor.execute("PRAGMA query_only = ON")
        
        with self.assertRaises(sqlite3.OperationalError):
            cursor.execute("COMMIT")
            
        # Reset for cleanup
        cursor.execute("PRAGMA query_only = OFF")
        self.conn.rollback()