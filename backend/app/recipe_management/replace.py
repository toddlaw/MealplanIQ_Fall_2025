"""
Provides logic for replacing a recipe in a meal plan and updating nutritional values.

@author: BCIT May 2025
"""

import pandas as pd
import ast
import time
from flask import jsonify
from app.generate_meal_plan import gen_shopping_list, insert_status_nutrient_info
from app.find_matched_recipe_and_update import update_nutrition_values

def replace_recipe_logic(data):
    """
    Replace a recipe in a specific position of a meal plan and update nutritional totals.

    Args:
        data (dict): JSON request payload containing:
            - meal_plan (dict): The current meal plan data structure.
            - recipe_id (dict): The new recipe ID dictionary with key 'id'.
            - day_index (int): Index of the day in the meal plan.
            - recipe_index (int): Index of the recipe within the day's recipe list.

    Returns:
        Response: A Flask JSON response containing the updated meal plan and replaced recipe ID,
                  or an error message if the new recipe is not found.
    """
    meal_plan = data.get("meal_plan")
    recipe_id = data.get("recipe_id")
    id = recipe_id.get("id")
    day_index = data.get("day_index")
    recipe_index = data.get("recipe_index")

    recipe_df = pd.read_csv("./meal_db/meal_database.csv")
    snack_recipes_df = recipe_df[recipe_df["meal_slot"] == "['snack']"]

    old_recipe = meal_plan["days"][day_index]["recipes"].pop(recipe_index)
    new_recipe_row = recipe_df.loc[recipe_df["number"] == int(id)]

    if new_recipe_row.empty:
        return jsonify({"error": "New recipe not found."}), 400

    new_recipe = new_recipe_row.iloc[0].to_dict()
    new_recipe = {k: (None if pd.isnull(v) else v) for k, v in new_recipe.items()}

    if new_recipe["meal_slot"] == 'Snack':
        new_recipe['instructions'] = ast.literal_eval(new_recipe['instructions'])
        new_recipe['ingredients_with_quantities'] = ast.literal_eval(new_recipe['ingredients_with_quantities'])

    new_recipe["id"] = int(new_recipe["number"])
    new_recipe["calories"] = int(new_recipe["energy_kcal"])
    new_recipe["prep_time"] = new_recipe["preptime"]
    new_recipe["meal_name"] = old_recipe["meal_name"]

    meal_plan = update_nutrition_values(meal_plan, old_recipe, "subtract", recipe_df, snack_recipes_df)
    meal_plan["days"][day_index]["recipes"].insert(recipe_index, new_recipe)
    meal_plan = update_nutrition_values(meal_plan, new_recipe, "add", recipe_df, snack_recipes_df)

    time.sleep(0.1)
    meal_plan = gen_shopping_list(meal_plan)
    meal_plan = insert_status_nutrient_info(meal_plan)
    time.sleep(0.1)

    return jsonify({"meal_plan": meal_plan, "id_replaced": new_recipe["number"]})
