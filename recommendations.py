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
        List of recommended books. Returns empty list if no preferences are provided.
    """
    # Return empty list if no preferences are provided
    if not preferences['genres'] and not preferences['authors']:
        return []
        
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
            
        # If no conditions (shouldn't happen due to earlier check), return empty list
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