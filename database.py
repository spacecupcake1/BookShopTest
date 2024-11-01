import sqlite3
from contextlib import contextmanager
import os

DATABASE_NAME = "library.db"

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    # Delete the existing database file if it exists
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)
        
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create Authors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')

        # Create Genres table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS genres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')

        # Create Books table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                author_id INTEGER,
                genre_id INTEGER,
                FOREIGN KEY (author_id) REFERENCES authors(id),
                FOREIGN KEY (genre_id) REFERENCES genres(id)
            )
        ''')
        
        conn.commit()