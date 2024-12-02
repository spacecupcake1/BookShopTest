# test_db.py
import unittest
import sqlite3

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
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
        
    def test_connection(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1")
        self.assertEqual(cursor.fetchone()[0], 1)
        
    def test_author_constraints(self):
        cursor = self.conn.cursor()
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO authors (name) VALUES (?)", ("",))
            
    def test_transaction_rollback(self):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO authors (name) VALUES (?)", ("Author 1",))
        self.conn.rollback()
        cursor.execute("SELECT COUNT(*) FROM authors")
        self.assertEqual(cursor.fetchone()[0], 0)
        
    def test_transaction_commit(self):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO authors (name) VALUES (?)", ("Author 1",))
        self.conn.commit()
        cursor.execute("SELECT name FROM authors")
        self.assertEqual(cursor.fetchone()['name'], "Author 1")

if __name__ == '__main__':
    unittest.main()