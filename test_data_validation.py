import unittest
from unittest.mock import patch
import sqlite3

class TestDataValidation(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key support
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
        cursor = self.conn.cursor()
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO authors (name) VALUES (?)", ("",))
        
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO authors (name) VALUES (?)", ("A" * 101,))

    def test_unique_constraint(self):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO genres (name) VALUES (?)", ("Test Genre",))
        self.conn.commit()
        
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO genres (name) VALUES (?)", ("Test Genre",))

    def test_foreign_key_constraint(self):
        cursor = self.conn.cursor()
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO books (title, author_id, genre_id)
                VALUES (?, ?, ?)
            """, ("Test Book", 999, 999))