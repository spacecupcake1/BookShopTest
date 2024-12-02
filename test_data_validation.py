import unittest
from unittest.mock import patch
import sqlite3

class TestDataValidation(unittest.TestCase):
    def setUp(self):
        """Tests for data validation and constraints"""
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

    def create_tables(self):
        self.conn.executescript('''
            CREATE TABLE authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK (length(name) > 0 AND length(name) <= 100)
            );
            CREATE TABLE genres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE CHECK (length(name) > 0)
            );
            CREATE TABLE books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL CHECK (length(title) > 0),
                description TEXT,
                author_id INTEGER NOT NULL,
                genre_id INTEGER NOT NULL,
                FOREIGN KEY (author_id) REFERENCES authors (id),
                FOREIGN KEY (genre_id) REFERENCES genres (id)
            );
        ''')
    
    def tearDown(self):
        self.conn.close()

    def test_name_constraints(self):
        """Test: Name field constraints (empty and length)"""
        cursor = self.conn.cursor()
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO authors (name) VALUES (?)", ("",))
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO authors (name) VALUES (?)", ("A" * 101,))

    def test_unique_constraint(self):
        """Test: Unique constraint on genre names"""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO genres (name) VALUES (?)", ("Test Genre",))
        self.conn.commit()
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO genres (name) VALUES (?)", ("Test Genre",))

    def test_foreign_key_constraint(self):
        """Test: Foreign key constraints on books table"""
        cursor = self.conn.cursor()
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO books (title, author_id, genre_id) VALUES (?, ?, ?)", 
                         ("Test Book", 999, 999))
            

    def test_successful_insert(self):
        """Test: Correct data insertion"""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO authors (name) VALUES (?)", ("Valid Author",))
        self.conn.commit()
        
        result = cursor.execute("SELECT name FROM authors WHERE name=?", ("Valid Author",)).fetchone()
        self.assertEqual(result['name'], "Valid Author")

    def test_update_data(self):
        """Test: Data update operation"""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO authors (name) VALUES (?)", ("Original Name",))
        self.conn.commit()
        
        cursor.execute("UPDATE authors SET name=? WHERE name=?", ("Updated Name", "Original Name"))
        self.conn.commit()
        
        result = cursor.execute("SELECT name FROM authors WHERE name=?", ("Updated Name",)).fetchone()
        self.assertEqual(result['name'], "Updated Name")