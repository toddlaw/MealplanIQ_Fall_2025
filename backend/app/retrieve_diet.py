import pandas as pd

def get_diet_plan(health_plan):
    """
    Called in ./backend/app/generate_meal_plan.py.
    Retrieves the diet plan information for a given health plan.
    :param health_plan: string of health plan
    :return: dict of diet plan details including ingredients, methods and nutrients
    """
    meal_db = pd.read_csv(f'./meal_db/meal_database.csv')
    recipe_id_list = list(meal_db['number'])

    if health_plan == 'lose_weight':
        return {
            "plan": "lose_weight",
            "nutrients" : {"nutrients": {"nutrient": ""}},
            "diet_score" : dict(zip(recipe_id_list, [1 for i in range(len(recipe_id_list))]))
        }

    diet_ingredients = pd.read_csv(f'./diets/{health_plan}/{health_plan}_ingreds.csv')
    diet_methods = pd.read_csv(f'./diets/{health_plan}/{health_plan}_methods.csv')
    diet_nutrients = pd.read_csv(f'./diets/{health_plan}/{health_plan}_nutrients.csv')
    diet_score = dict(zip(recipe_id_list, meal_db[f'{health_plan}_score']))


    return {
        "plan": health_plan,
        "ingredients": diet_ingredients.to_dict(),
        "methods": diet_methods.to_dict(),
        "nutrients": diet_nutrients.to_dict(),
        "diet_score": diet_score
    }
