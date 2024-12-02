from database import get_db_connection
from models import BookCreate, AuthorCreate, GenreCreate

def create_author(author: AuthorCreate):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO authors (name) VALUES (?)', (author.name,))
        conn.commit()
        return {"id": cursor.lastrowid, "name": author.name}

def get_authors(skip: int = 0, limit: int = 10):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM authors LIMIT ? OFFSET ?', (limit, skip))
        authors = [dict(row) for row in cursor.fetchall()]
        
        # Get books for each author
        for author in authors:
            cursor.execute('SELECT * FROM books WHERE author_id = ?', (author['id'],))
            author['books'] = [dict(row) for row in cursor.fetchall()]
        
        return authors

def get_author(author_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM authors WHERE id = ?', (author_id,))
        author = cursor.fetchone()
        if author:
            author_dict = dict(author)
            cursor.execute('SELECT * FROM books WHERE author_id = ?', (author_id,))
            author_dict['books'] = [dict(row) for row in cursor.fetchall()]
            return author_dict
        return None

def create_genre(genre: GenreCreate):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO genres (name) VALUES (?)', (genre.name,))
        conn.commit()
        return {"id": cursor.lastrowid, "name": genre.name}

def get_genres(skip: int = 0, limit: int = 10):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM genres LIMIT ? OFFSET ?', (limit, skip))
        return [dict(row) for row in cursor.fetchall()]

def get_genre(genre_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM genres WHERE id = ?', (genre_id,))
        genre = cursor.fetchone()
        return dict(genre) if genre else None

def create_book(book: BookCreate):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO books (title, description, author_id, genre_id) VALUES (?, ?, ?, ?)',
            (book.title, book.description, book.author_id, book.genre_id)
        )
        conn.commit()
        return {
            "id": cursor.lastrowid,
            "title": book.title,
            "description": book.description,
            "author_id": book.author_id,
            "genre_id": book.genre_id
        }

def get_books(skip: int = 0, limit: int = 10):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                b.*,
                a.name as author_name,
                g.name as genre_name
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.id
            LEFT JOIN genres g ON b.genre_id = g.id
            LIMIT ? OFFSET ?
        ''', (limit, skip))
        return [dict(row) for row in cursor.fetchall()]

def get_book(book_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                b.*,
                a.name as author_name,
                g.name as genre_name
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.id
            LEFT JOIN genres g ON b.genre_id = g.id
            WHERE b.id = ?
        ''', (book_id,))
        book = cursor.fetchone()
        return dict(book) if book else None

def get_books_by_genre(genre_id: int, skip: int = 0, limit: int = 10):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                b.*,
                a.name as author_name,
                g.name as genre_name
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.id
            LEFT JOIN genres g ON b.genre_id = g.id
            WHERE b.genre_id = ?
            LIMIT ? OFFSET ?
        ''', (genre_id, limit, skip))
        return [dict(row) for row in cursor.fetchall()]