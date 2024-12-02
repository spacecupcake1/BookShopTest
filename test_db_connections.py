import unittest
import sqlite3

class TestDatabaseConnections(unittest.TestCase):
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
        self.assertIsInstance(self.conn, sqlite3.Connection)
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1")
        self.assertEqual(cursor.fetchone()[0], 1)

    def test_multiple_connections(self):
        conn2 = sqlite3.connect(':memory:')
        self.assertNotEqual(id(self.conn), id(conn2))
        conn2.close()

    def test_connection_row_factory(self):
        self.assertEqual(self.conn.row_factory, sqlite3.Row)

