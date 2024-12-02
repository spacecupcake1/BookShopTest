import unittest
from unittest.mock import patch
from database import init_db

class BaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patcher = patch('database.DATABASE_NAME', ':memory:')
        cls.patcher.start()
        
    def setUp(self):
        init_db()
        
    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()