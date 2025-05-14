"""
Handles loading recipe data from a CSV file into an in-memory global variable.
"""

import csv

recipes = []

def load_recipe_data():
    """
    Load all recipes from the `meal_database.csv` file into the global `recipes` list.

    This function reads the CSV into a list of dictionaries, where each dictionary represents a recipe.

    If an error occurs while reading the file, it will log the error and reset `recipes` to an empty list.
    """
    global recipes
    try:
        with open('./meal_db/meal_database.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            recipes = list(reader)
            print(f"Loaded {len(recipes)} recipes from meal_database.csv")
    except Exception as e:
        print(f"Error loading meal_database.csv: {e}")
        recipes = []

# Load recipes immediately on module import
load_recipe_data()
