from typing import List, Dict
from database import get_db_connection
import sqlite3

def get_book_recommendations(preferences: Dict) -> List[Dict]:
    """
    Get book recommendations based on user preferences.
    
    Args:
        preferences: Dict containing:
            - genres: List of preferred genres
            - authors: List of preferred authors
            - max_results: Maximum number of recommendations to return
    
    Returns:
        List of recommended books. Returns empty list if no preferences are provided.
        
    Raises:
        TypeError: If preferences have invalid format
        ValueError: If max_results is invalid
        Exception: For database errors
    """
    # Input validation
    if not isinstance(preferences.get('genres'), list) or not isinstance(preferences.get('authors'), list):
        raise TypeError("Genres and authors must be lists")
        
    if preferences.get('max_results', 0) <= 0:
        return []

    # Return empty list if no preferences are provided
    if not preferences['genres'] and not preferences['authors']:
        return []
        
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Build the query based on available preferences
            conditions = []
            params = []
            
            if preferences['genres']:
                conditions.append(f"g.name IN ({','.join(['?'] * len(preferences['genres']))})")
                params.extend(preferences['genres'])
                
            if preferences['authors']:
                conditions.append(f"a.name IN ({','.join(['?'] * len(preferences['authors']))})")
                params.extend(preferences['authors'])
                
            if not conditions:
                return []
                
            query = """
            SELECT DISTINCT 
                b.id,
                b.title,
                b.description,
                a.name as author,
                g.name as genre
            FROM books b
            JOIN authors a ON b.author_id = a.id
            JOIN genres g ON b.genre_id = g.id
            WHERE {}
            LIMIT ?
            """.format(" OR ".join(conditions))
            
            params.append(preferences['max_results'])
            
            cursor.execute(query, params)
            
            return [{
                'id': row['id'],
                'title': row['title'],
                'description': row['description'],
                'author': row['author'],
                'genre': row['genre']
            } for row in cursor.fetchall()]
            
    except sqlite3.Error as e:
        raise Exception(f"Database error: {str(e)}")