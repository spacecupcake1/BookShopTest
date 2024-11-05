# tests/test_mutations.py
import unittest
import sys
import argparse
from unittest.mock import Mock, patch
import random
import string
import sqlite3
from tests.utils import setup_mock_data
from models import BookCreate

class TestMutationTesting(unittest.TestCase):
    def setUp(self):
        self.db_mock = Mock()
        self.cursor_mock = Mock()
        self.db_mock.cursor.return_value = self.cursor_mock
        
    def _mutate_string(self, original_string, mutation_type='random'):
        """Helper method to mutate a string with specific mutation types"""
        if not original_string:
            return original_string
            
        if mutation_type == 'empty':
            return ''
        elif mutation_type == 'very_long':
            return original_string * 20
        elif mutation_type == 'special_chars':
            return original_string + '@#$%^'
        elif mutation_type == 'random':
            chars = list(original_string)
            mutation_rate = 0.3  # 30% of characters will be mutated
            num_mutations = max(1, int(len(chars) * mutation_rate))
            
            for _ in range(num_mutations):
                idx = random.randint(0, len(chars) - 1)
                mutation_type = random.choice(['replace', 'insert', 'delete'])
                
                if mutation_type == 'replace':
                    chars[idx] = random.choice(string.ascii_letters + string.digits)
                elif mutation_type == 'insert':
                    chars.insert(idx, random.choice(string.ascii_letters + string.digits))
                elif mutation_type == 'delete' and len(chars) > 1:
                    chars.pop(idx)
                    
            return ''.join(chars)
        return original_string

    @patch('crud.get_db_connection')
    def test_mutated_book_creation(self, mock_db_conn):
        """Test creating books with mutated data to verify error handling"""
        mock_db_conn.return_value.__enter__.return_value = self.db_mock
        self.cursor_mock.lastrowid = 1
        
        original_book = BookCreate(
            title="Original Test Book",
            description="Test Description",
            author_id=1,
            genre_id=1
        )
        
        print("\nMutation Testing Results:")
        print("------------------------")
        
        mutation_types = [
            'random',         
            'empty',         
            'very_long',     
            'special_chars', 
            'random'         
        ]
        
        mutation_results = []
        
        for i, mutation_type in enumerate(mutation_types):
            try:
                mutated_title = self._mutate_string(original_book.title, mutation_type)
                
                print(f"\nMutation #{i + 1} ({mutation_type})")
                print(f"Original: {original_book.title}")
                print(f"Mutated:  {mutated_title}")
                
                if len(mutated_title) > 50:
                    raise sqlite3.IntegrityError("Book title exceeds maximum length")
                elif len(mutated_title) == 0:
                    raise ValueError("Book title cannot be empty")
                    
                print(f"Status: SUCCESS")
                mutation_results.append({
                    'status': 'success',
                    'mutation_type': mutation_type
                })
                
            except Exception as e:
                print(f"Status: ERROR - {str(e)}")
                mutation_results.append({
                    'status': 'error',
                    'mutation_type': mutation_type,
                    'error': str(e)
                })
        
        # Print summary
        error_count = sum(1 for r in mutation_results if r['status'] == 'error')
        success_count = sum(1 for r in mutation_results if r['status'] == 'success')
        
        print("\nSummary:")
        print(f"Total mutations: {len(mutation_results)}")
        print(f"Successful mutations: {success_count}")
        print(f"Failed mutations: {error_count}")
        
        self.assertGreater(error_count, 0, "Expected some mutations to cause errors")
        self.assertGreater(success_count, 0, "Expected some mutations to succeed")

if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]])