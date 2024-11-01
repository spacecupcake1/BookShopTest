from database import get_db_connection

def seed_database():
    """Seed the database with initial data."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Seed Authors
        authors_data = [
            ("J.K. Rowling",),
            ("George R.R. Martin",)
        ]
        cursor.executemany('INSERT INTO authors (name) VALUES (?)', authors_data)
        
        # Seed Genres
        genres_data = [
            ("Fantasy",),
            ("Science Fiction",)
        ]
        cursor.executemany('INSERT INTO genres (name) VALUES (?)', genres_data)
        
        # Seed Books
        books_data = [
            ("Harry Potter and the Philosopher's Stone", 
             "The first book in the Harry Potter series", 1, 1),
            ("A Game of Thrones", 
             "The first book of A Song of Ice and Fire series", 2, 1),
            ("Harry Potter and the Chamber of Secrets", 
             "The second book in the Harry Potter series", 1, 1),
            ("A Clash of Kings", 
             "The second book of A Song of Ice and Fire series", 2, 1)
        ]
        cursor.executemany('''
            INSERT INTO books (title, description, author_id, genre_id) 
            VALUES (?, ?, ?, ?)
        ''', books_data)
        
        conn.commit()
        
        return get_db_stats()

def get_db_stats():
    """Get statistics about the seeded data."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get authors
        cursor.execute('SELECT name FROM authors')
        authors = [row[0] for row in cursor.fetchall()]
        
        # Get genres
        cursor.execute('SELECT name FROM genres')
        genres = [row[0] for row in cursor.fetchall()]
        
        # Get books with author names
        cursor.execute('''
            SELECT b.title, a.name as author
            FROM books b
            JOIN authors a ON b.author_id = a.id
        ''')
        books = [(row[0], row[1]) for row in cursor.fetchall()]
        
        return {
            "authors": authors,
            "genres": genres,
            "books": books
        }