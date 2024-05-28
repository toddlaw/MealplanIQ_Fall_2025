
def find_matched_recipe_and_update(response, recipe_id):
    """
    Called in ./backend/app/routes.py.
    Find the recipe in the response and update the recipe's status to 'matched'.
    :param response: JSON object containing the meal plan
    :param recipe_id: string of the recipe ID
    :return: updated JSON object containing the meal plan
    """
    recipe_to_replce = {}
    for day in response["meal_plan"]:
        for recipe in day["meals"]:
            if recipe["recipe_id"] == recipe_id:
                recipe_to_replce = recipe["recipe_id"]
    