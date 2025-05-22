"""
Provides logic for retrieving a specific recipe's details by its ID.

@author: BCIT May 2025
"""

from flask import jsonify
from app.recipe_management.load_data import recipes

def get_recipe_logic(recipe_id):
    """
    Retrieve a recipe's detailed information by its unique recipe ID.

    Args:
        recipe_id (int): The unique numeric ID of the recipe to retrieve.

    Returns:
        Response: A Flask JSON response containing the recipe details if found,
                  or a 404 error JSON response if not found.
    """
    recipe = next((r for r in recipes if int(r.get('number', 0)) == recipe_id), None)
    if recipe:
        return jsonify({
            'id': int(recipe.get('number', 0)),
            'title': recipe.get('title', ''),
            'calories': float(recipe.get('energy_kcal', 0)),
            'region': recipe.get('region', ''),
            'prep_time': recipe.get('preptime', ''),
            'ingredients': recipe.get('ingredients', ''),
            'instructions': recipe.get('instructions', '')
        })
    return jsonify({'error': 'Recipe not found'}), 404
