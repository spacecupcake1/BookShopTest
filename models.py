from dataclasses import dataclass
from pydantic import BaseModel
from typing import Optional, List

class BookCreate(BaseModel):
    title: str
    description: Optional[str] = None
    author_id: int
    genre_id: int

class BookResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    author_id: int
    genre_id: int

class AuthorCreate(BaseModel):
    name: str

class AuthorResponse(BaseModel):
    id: int
    name: str
    books: List[BookResponse] = []

class GenreCreate(BaseModel):
    name: str

class GenreResponse(BaseModel):
    id: int
    name: str