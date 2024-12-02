import sqlite3
from contextlib import contextmanager
import os

DATABASE_NAME = 'library.db'

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.executescript('''
        DROP TABLE IF EXISTS books;
        DROP TABLE IF EXISTS authors;
        DROP TABLE IF EXISTS genres;

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
    conn.close()

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()