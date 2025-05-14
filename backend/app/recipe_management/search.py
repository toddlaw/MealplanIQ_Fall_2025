"""
Provides logic for searching recipes by title, ingredients, region, or subregion.
"""

import re
from flask import jsonify
from app.recipe_management.load_data import recipes

def search_recipes_logic(query, exact_match):
    """
    Search for recipes based on a query string, optionally requiring exact matches.

    Args:
        query (str): The search query string.
        exact_match (bool): Whether to require exact word matches (True) or allow partial matches (False).

    Returns:
        Response: A Flask JSON response containing a list of matched recipes, each with selected fields.
                  Returns an empty list if no query is provided or no matches found.
    """
    query = query.lower().strip()
    if not query:
        return jsonify([])

    matched = []
    for recipe in recipes:
        title = recipe.get('title', '').lower()
        ingredients = recipe.get('ingredients', '').lower()
        region = recipe.get('region', '').lower()
        subregion = recipe.get('subregion', '').lower()

        match = False
        if exact_match:
            terms = query.split()
            match = all(
                any(re.search(rf'\b{re.escape(term)}\b', field)
                    for field in [title, ingredients])
                for term in terms
            )
        else:
            match = any(query in field for field in [title, ingredients, region, subregion])

        if match:
            try:
                matched_recipe = {
                    'id': int(recipe.get('number', 0)),
                    'title': recipe.get('title', ''),
                    'calories': float(recipe.get('energy_kcal', 0)),
                    'region': recipe.get('region', ''),
                    'prep_time': recipe.get('preptime', ''),
                    'cook_time': recipe.get('cooktime', '')
                }
                matched.append(matched_recipe)
            except ValueError:
                continue

    return jsonify(matched)
