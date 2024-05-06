import pandas as pd

def apply_user_prefs(fav_cuisines, diet_contraint, religious_constraint, liked_foods, disliked_foods, allergies):
    """
    Called in ./backend/app/generate_meal_plan.py.
    Applies the user preferences to the meal database and calculates a score for each recipe.
    :param fav_cuisines: string list of favourite cuisines
    :param diet_constraint: string of dietary constraint
    :param religious_constraint: string of religious constraint
    :param liked_foods: string list of liked foods
    :param disliked_foods: string list of disliked foods
    :param allergies: string list of allergies
    :return: dataframe of recipes with scores
    """
    recipes = pd.read_csv('./meal_db/meal_database.csv')
    diet_restrictions = get_diet_restrictions(diet_contraint)
    religious_restrictions = get_religious_restrictions(religious_constraint)
    restrictions_for_allergies = get_restrictions_for_allergies(allergies)

    fav_cuisines = [cuisine.lower() for cuisine in fav_cuisines]
    liked_foods = [food.lower() for food in liked_foods]
    disliked_foods = [food.lower() for food in disliked_foods]

    # Skip the first row as it is the column names
    recipes['score'] = recipes.apply(
        lambda row: calculate_scores(row, fav_cuisines, diet_restrictions, religious_restrictions, liked_foods, disliked_foods, 
                                     restrictions_for_allergies), 
        axis = 1)
    
    return recipes

def calculate_scores(row, fav_cuisines, diet_restrictions, religious_restrictions, liked_foods, disliked_foods, 
                     restrictions_for_allergies):
    """
    Called in ./backend/app/apply_user_prefs_to_meal_database.py.
    Calculates a score for each recipe based on the user preferences.
    :param row: dataframe row
    :param fav_cuisines: string list of favourite cuisines
    :param diet_restrictions: string list of diet restrictions
    :param religious_restrictions: string list of religious restrictions
    :param liked_foods: string list of liked foods
    :param disliked_foods: string list of disliked foods
    :return: numeric score for recipe
    """
    recipe_ingredients = row['ingredients'].strip("[]'").split("', '")
    recipe_ingredients = [ingredient.lower() for ingredient in recipe_ingredients]
    recipe_country = row['country'].lower()
    recipe_name = row['title'].lower()
    score = 1

    # Allergies restrictions
    for allergy_restrictions in restrictions_for_allergies:
        if contains_invalid_ingredient(recipe_ingredients, allergy_restrictions):
            return 0

    # Diet and religious restrictions
    if (contains_invalid_ingredient(recipe_ingredients, diet_restrictions) or 
        contains_invalid_ingredient(recipe_ingredients, religious_restrictions)):
        return 0

    # Favourite cuisines
    if recipe_country in fav_cuisines:
        score += 1

    # Liked foods
    for food in liked_foods:
        if food in recipe_name:
            score += 1
    
    # Disliked foods
    for food in disliked_foods:
        if food in recipe_ingredients:
            score -= 1

    return score

def contains_invalid_ingredient(recipe_ingredients, restricted_ingredients):
    """
    Called in ./backend/app/apply_user_prefs_to_meal_database.py.
    Checks if a recipe contains an ingredient that a person cannot eat based on their constraints.
    :param recipe_ingredients: string list of recipe ingredients
    :param restricted_ingredients: string list of restricted ingredients
    :return: boolean indicating if a recipe contains a restricted ingredient
    """
    for restricted_ingredient in restricted_ingredients:
        if restricted_ingredient in recipe_ingredients:
            return True
        
    return False

def get_diet_restrictions(diet_constraint):
    """
    Called in ./backend/app/apply_user_prefs_to_meal_database.py.
    Returns a list of ingredients that a person cannot eat based on their dietary constraint.
    :param: diet_constraint: string of dietary constraint
    :return: list of restricted ingredients
    """
    diet_restrictions = {
        'vegan': ['beef', 'chicken', 'pork', 'bacon', 'ham', 'lamb', 'goat', 'turkey', 'pigeon', 'rabbit', 'squirrel', 'camel', 
                  'deer', 'kangaroo' 'salmon', 'fish', 'tuna', 'lobster', 'crab', 'oyster', 'mussel', 'scallop', 'shrimp', 'egg', 
                  'milk', 'cheese', 'yogurt', 'cream', 'butter'],
        'pescatarian': ['beef', 'chicken', 'pork', 'bacon', 'ham', 'lamb', 'goat', 'turkey', 'pigeon', 'rabbit', 'squirrel', 
                        'camel', 'deer', 'kangaroo', 'egg', 'milk', 'cheese', 'yogurt', 'cream', 'butter'],
        'vegetarian': ['pigeon', 'lobster', 'oyster', 'kangaroo', 'shrimp', 'ham', 'turkey', 'beef', 'lamb', 'camel', 'squirrel', 
                       'chicken', 'salmon', 'fish', 'bacon', 'goat', 'deer', 'pork', 'crab', 'butter', 'mussel', 'tuna', 'rabbit', 
                       'scallop'],
        'none': []
    }
    
    return diet_restrictions[diet_constraint]

def get_religious_restrictions(religious_contraint):
    """
    Called in ./backend/app/apply_user_prefs_to_meal_database.py.
    Returns a list of ingredients that a person cannot eat based on their religious constraint.
    :param: religious_constraint: string of religious constraint
    :return: list of restricted ingredients
    """
    religious_restrictions = {
        'halal': ['wine', 'beer', 'pork', 'bacon', 'ham'],
        'kosher': ['pork', 'bacon', 'ham', 'rabbit', 'squirrel', 'camel', 'deer', 'kangaroo', 'shrimp', 'crab', 'oyster', 
                   'lobster', 'scallop', 'mussel'],
        'none': []
    }

    return religious_restrictions[religious_contraint]

def get_restrictions_for_allergies(allergies):
    """
    Called in ./backend/app/apply_user_prefs_to_meal_database.py.
    Returns a list of lists with restricted ingredients that a person cannot eat based on their allergies.
    :param: allergies: string list of allergies
    """
    allergies = [allergy.lower() for allergy in allergies]

    allergy_restrictions = {
        'peanut': ['peanuts', 'peanut'],
        'tree nut': ['almond', 'almonds', 'cashew', 'cashews', 'chestnut', 'chestnuts', 'hazelnut', 'hazelnuts', 'macadamia', 
                     'macadamias', 'pecan', 'pecans', 'pine nut', 'pine nuts', 'pistachio', 'pistachios', 'walnut', 'walnuts'],
        'dairy': ['milk', 'cheese', 'yogurt', 'cream', 'butter'],
        'egg': ['egg', 'eggs'],
        'gluten': ['wheat', 'bread', 'pasta', 'noodles', 'noodle', 'couscous', 'cereal', 'flour', 'breadcrumbs', 'breadcrumbs' 
                   'cracker', 'crackers'],
        'grain': ['wheat', 'barley', 'rye', 'rice', 'oats', 'oat' 'corn', 'bread', 'pasta', 'noodles', 'couscous', 'cereal', 
                  'flour'],
        'soy': ['soy', 'soya', 'soybean', 'soybeans', 'tofu', 'edamame', 'miso', 'natto', 'soy sauce', 'soya sauce' 'soybean oil'],
        'shellfish': ['crab', 'crabs', 'lobster', 'shrimp', 'shrimps', 'prawn', 'prawns', 'clam', 'clams', 'mussel', 'mussles', 
                      'oyster', 'oysters', 'scallop', 'scallops'],
        'seafood': ['crab', 'crabs', 'lobster', 'shrimp', 'shrimps', 'prawn', 'prawns', 'clam', 'clams', 'mussel', 'mussles', 
                    'oyster', 'oysters', 'scallop', 'scallops', 'salmon', 'fish', 'tuna'],
        'sesame': ['sesame', 'sesame seed', 'sesame seeds', 'tahini', 'sesame oil'],
        'sulfite': ['sulfite', 'sulfites', 'sulphite', 'sulphites', 'sulfur dioxide', 'sulphur dioxide'],
        'wheat': ['wheat', 'bread', 'pasta', 'noodles', 'noodle', 'couscous', 'cereal', 'flour', 'breadcrumbs', 'breadcrumbs', 
                  'cracker', 'crackers'],
    }
    
    user_allergies = []

    for allergy in allergies:
        user_allergies.append(allergy_restrictions[allergy])

    return user_allergies
