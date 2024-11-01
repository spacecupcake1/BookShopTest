from fastapi import FastAPI, HTTPException
from typing import List
import socket
import sys

from models import (
    BookCreate, BookResponse,
    AuthorCreate, AuthorResponse,
    GenreCreate, GenreResponse
)
from crud import (
    create_book, get_books, get_book,
    create_author, get_authors, get_author,
    create_genre, get_genres, get_genre,
    get_books_by_genre
)
from database import init_db
from seeder import seed_database, get_db_stats

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/seed")
async def seed_data():
    """Endpoint to trigger database seeding"""
    stats = seed_database()
    return {
        "message": "Database seeded successfully",
        "data": stats
    }

@app.get("/stats")
async def get_stats():
    """Get current database statistics"""
    return get_db_stats()

@app.on_event("startup")
async def startup_event():
    init_db()

@app.post("/genres/", response_model=GenreResponse)
async def create_new_genre(genre: GenreCreate):
    return create_genre(genre)

@app.get("/genres/", response_model=List[GenreResponse])
async def get_genres_list(skip: int = 0, limit: int = 10):
    return get_genres(skip=skip, limit=limit)

@app.get("/genres/{genre_id}", response_model=GenreResponse)
async def get_genre_by_id(genre_id: int):
    genre = get_genre(genre_id)
    if genre is None:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre

@app.get("/genres/{genre_id}/books", response_model=List[BookResponse])
async def get_books_by_genre_id(genre_id: int, skip: int = 0, limit: int = 10):
    return get_books_by_genre(genre_id, skip=skip, limit=limit)


@app.post("/books/", response_model=BookResponse)
async def create_new_book(book: BookCreate):
    return create_book(book)

@app.get("/books/", response_model=List[BookResponse])
async def get_books_list(skip: int = 0, limit: int = 10):
    return get_books(skip=skip, limit=limit)

@app.get("/books/{book_id}", response_model=BookResponse)
async def get_book_by_id(book_id: int):
    book = get_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/authors/", response_model=AuthorResponse)
async def create_new_author(author: AuthorCreate):
    return create_author(author)

@app.get("/authors/", response_model=List[AuthorResponse])
async def get_authors_list(skip: int = 0, limit: int = 10):
    return get_authors(skip=skip, limit=limit)

@app.get("/authors/{author_id}", response_model=AuthorResponse)
async def get_author_by_id(author_id: int):
    author = get_author(author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


def find_free_port(start_port: int = 8000, max_attempts: int = 100) -> int:
    """Find a free port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find a free port after {max_attempts} attempts")

if __name__ == "__main__":
    import uvicorn
    
    try:
        port = find_free_port()
        print(f"Starting server on port {port}")
        uvicorn.run(app, host="127.0.0.1", port=port)
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)