# recommendations.py
from typing import List, Dict
from database import get_db_connection

def get_book_recommendations(preferences: Dict) -> List[Dict]:
    """
    Get book recommendations based on user preferences.
    
    Args:
        preferences: Dict containing:
            - genres: List of preferred genres
            - authors: List of preferred authors
            - max_results: Maximum number of recommendations to return
    
    Returns:
        List of recommended books
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
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
        WHERE g.name IN ({}) OR a.name IN ({})
        LIMIT ?
        """.format(
            ','.join(['?'] * len(preferences['genres'])),
            ','.join(['?'] * len(preferences['authors']))
        )
        
        params = [*preferences['genres'], *preferences['authors'], preferences['max_results']]
        cursor.execute(query, params)
        
        recommendations = []
        for row in cursor.fetchall():
            recommendations.append({
                'id': row['id'],
                'title': row['title'],
                'description': row['description'],
                'author': row['author'],
                'genre': row['genre']
            })
            
        return recommendations