import argparse
import sqlite3
from unittest.mock import Mock
from models import BookCreate, AuthorCreate, GenreCreate

class BookshopTestRunner:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Run Bookshop Tests')
        self.setup_arguments()
        
    def setup_arguments(self):
        self.parser.add_argument(
            '--test-type',
            choices=['db-mock', 'time-freeze', 'tdd', 'mutation'],
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
        self.parser.add_argument(
            '--mutation-rate',
            type=float,
            default=0.2,
            help='Rate of mutation for mutation testing (0.0 to 1.0)'
        )

def get_test_suite(test_type):
    """Return the appropriate test suite based on test type"""
    if test_type == 'mutation':
        from tests.test_mutations import setup_mutation_test
        return setup_mutation_test()
    # Add other test types here as needed
    return None

def setup_mock_data():
    """Set up mock data for testing"""
    mock_data = {}
    mock_data['books'] = [
        BookCreate(
            title="Test Book 1",
            description="Description 1",
            author_id=1,
            genre_id=1
        ).model_dump(),  # Convert to dict for easier handling
        BookCreate(
            title="Test Book 2",
            description="Description 2",
            author_id=2,
            genre_id=1
        ).model_dump()
    ]
    
    mock_data['authors'] = [
        AuthorCreate(name="Test Author 1").model_dump(),
        AuthorCreate(name="Test Author 2").model_dump()
    ]
    
    mock_data['genres'] = [
        GenreCreate(name="Fantasy").model_dump(),
        GenreCreate(name="Science Fiction").model_dump()
    ]
    
    return mock_data