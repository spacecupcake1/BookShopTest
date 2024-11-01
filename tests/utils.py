import argparse
from unittest.mock import Mock
from models import BookCreate, AuthorCreate, GenreCreate

class BookshopTestRunner:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Run Bookshop Tests')
        self.setup_arguments()
        
    def setup_arguments(self):
        self.parser.add_argument(
            '--test-type',
            choices=['db-mock', 'time-freeze', 'tdd'],
            help='Type of test to run'
        )
        self.parser.add_argument(
            '--mock-data',
            action='store_true',
            help='Use mock data instead of test database'
        )
        self.parser.add_argument(
            '--time-freeze',
            type=str,
            help='Freeze time to specified datetime (format: YYYY-MM-DD)'
        )
        self.parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed test output'
        )

def setup_mock_data():
    mock_data = {}
    mock_data['books'] = [
        BookCreate(
            title="Test Book 1",
            description="Description 1",
            author_id=1,
            genre_id=1
        ),
        BookCreate(
            title="Test Book 2",
            description="Description 2",
            author_id=2,
            genre_id=1
        )
    ]
    
    mock_data['authors'] = [
        AuthorCreate(name="Test Author 1"),
        AuthorCreate(name="Test Author 2")
    ]
    
    mock_data['genres'] = [
        GenreCreate(name="Fantasy"),
        GenreCreate(name="Science Fiction")
    ]
    
    return mock_data