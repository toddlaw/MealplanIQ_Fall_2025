import pandas as pd


def apply_user_prefs(fav_cuisines, diet_contraint, religious_constraint, liked_foods, disliked_foods, allergies, recipes):
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
    # recipes = pd.read_csv('./meal_db/meal_database.csv')
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
        axis=1)
    # print("-----------returned recipes before removing 0 fit-to-preference score\n", recipes)
    recipes = recipes[recipes['score'] > 0]

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
    recipe_ingredients = [ingredient.lower()
                          for ingredient in recipe_ingredients]
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
                  'eggs', 'egg yolk', 'egg white', 'milk', 'cheese', 'yogurt', 'cream', 'butter'],
        'pescatarian': ['beef', 'chicken', 'pork', 'bacon', 'ham', 'lamb', 'goat', 'turkey', 'pigeon', 'rabbit', 'squirrel',
                        'camel', 'deer', 'kangaroo', 'egg', 'eggs', 'egg yolk', 'egg white', 'milk', 'cheese', 'yogurt', 'cream', 'butter'],
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
    'peanut': [
        "peanut",
        "peanuts",
        "peanut butter",
        "creamy peanut butter",
        "peanut oil",
        "peanut sauce",
        "roasted peanuts",
    ],

    'tree nut': [
        "almond",
        "almonds",
        "almond butter",
        "almond milk",
        "sliced almonds",
        "slivered almonds",
        "toasted almonds",
        "cashew",
        "cashews",
        "cashew nuts",
        "cashews - roasted and salted",
        "cashews - roasted unsalted",
        "raw cashews - whole",
        "pecan",
        "pecans",
        "toasted pecans",
        "pine nut",
        "pine nuts",
        "toasted pine nuts",
        "walnut",
        "walnuts",
        "nuts",
        "coconut flakes",
        "shredded coconut",
        "toasted coconut flakes",
        "coconut milk",
        "coconut oil",
    ],

    'dairy': [
        "butter",
        "unsalted butter",
        "clarified butter",
        "clarified butter (ghee)",
        "buttermilk",
        "milk",
        "milk - one percent",
        "whole milk",
        "warm milk",
        "sweetened condensed milk",
        "half-and-half",
        "cream",
        "heavy cream",
        "heavy whipping cream",
        "cheese",
        "cream cheese",
        "mascarpone cheese",
        "ricotta cheese",
        "whole milk ricotta cheese",
        "brie cheese",
        "blue cheese",
        "blue cheese crumbles",
        "cheddar cheese",
        "cheddar cheese - shredded",
        "sharp cheddar cheese",
        "sharp cheddar cheese - shredded",
        "gruyere cheese",
        "gruyere cheese - shredded",
        "gruyère cheese",
        "feta cheese",
        "goat cheese",
        "gorgonzola cheese",
        "halloumi cheese",
        "mozzarella cheese",
        "fresh mozzarella",
        "monterey jack cheese",
        "monterey jack cheese - shredded",
        "parmesan cheese",
        "grated parmesan cheese",
        "parmigiano-reggiano cheese",
        "parmesan cheese rind",
        "queso fresco",
        "queso fresco cheese",
        "queso fresco cheese - shredded",
        "mexican melting cheese",
        "mexican melting cheese (oaxaca or quesadilla)",
        "cotija cheese",
        "reblochon cheese",
        "swiss cheese",
        "yogurt",
        "greek yogurt",
        "plain greek yogurt",
        "plain yogurt",
        "vanilla greek yogurt",
        "sour cream",
        "crema mexicana",
        "crema mexicana (mexican sour cream)",
        "ice cream",
        "vanilla ice cream",
        "hollandaise sauce",
    ],

    'egg': [
        "ajitsuke tamago (marinated soft-boiled eggs)",
        "egg - fried",
        "egg - large",
        "egg noodles",
        "egg white - large",
        "egg whites - large",
        "egg whites",
        "egg yolk - large",
        "egg yolk",
        "egg yolks",
        "egg",
        "eggs - large",
        "eggs",
        "fried eggs - large",
        "fried or steamed eggs",
        "hard-boiled eggs",
    ],

    'gluten': [
        "all-purpose flour",
        "bagel",
        "baguette bread - large",
        "baguette",
        "bread - sourdough",
        "bread - white",
        "bread - whole wheat",
        "bread cubes",
        "bread",
        "breadcrumbs",
        "cereal",
        "cheerios oat crunch",
        "cheerios",
        "ciabatta bread",
        "couscous",
        "crackers",
        "day-old bread",
        "ditalini pasta",
        "elbow macaroni",
        "fettuccine",
        "flour tortilla",
        "flour tortillas - large",
        "flour tortillas",
        "flour",
        "french bread",
        "jumbo pasta shells",
        "lasagna noodles",
        "linguine",
        "lo mein noodles - dried",
        "lo mein noodles",
        "macaroni",
        "naan",
        "noodles",
        "pasta (long, such as spaghetti, linguine, or fettuccine)",
        "pasta (such as penne or fusilli)",
        "pasta (such as penne or spaghetti)",
        "pasta",
        "penne pasta",
        "phyllo dough",
        "pie crust",
        "pizza dough",
        "ramen noodles",
        "rigatoni pasta",
        "semolina flour",
        "shredded wheat",
        "small pasta",
        "spaghetti",
        "special k cereal",
        "tagliatelle",
        "wheat",
        "white bread",
        "whole grain bread",
        "whole grain tortilla",
        "ziti pasta",
    ],

    'grain': [
        "all-purpose flour",
        "arborio rice",
        "basmati rice",
        "bread - sourdough",
        "bread - white",
        "bread - whole wheat",
        "bread",
        "breadcrumbs",
        "brown rice",
        "cereal",
        "couscous",
        "flour tortilla",
        "flour tortillas - large",
        "flour tortillas",
        "flour",
        "long-grain white rice",
        "macaroni",
        "millet",
        "oats",
        "pasta",
        "penne pasta",
        "quinoa",
        "ramen noodles",
        "rice noodles",
        "rice",
        "rigatoni pasta",
        "semolina flour",
        "sorghum",
        "spaghetti",
        "tagliatelle",
        "wheat",
        "white rice - cooked",
        "white rice",
        "whole grain bread",
        "whole grain tortilla",
        "wild rice",
        "ziti pasta",
    ],

    'soy': [
        "edamame",
        "firm tofu",
        "miso paste",
        "silken tofu",
        "soft tofu",
        "soy milk",
        "soy sauce - light",
        "soy sauce - low sodium",
        "soy sauce",
        "soybean sprouts",
        "soybeans",
        "tofu",
    ],

    'shellfish': [
        "assorted shellfish",
        "calamari",
        "clam juice",
        "clams",
        "fresh clams",
        "littleneck clams",
        "crab",
        "lump crab meat",
        "cooked octopus",
        "mussels",
        "oyster sauce",
        "sea scallops",
        "scallops - dry packed",
        "shrimp - medium",
        "shrimp",
        "shrimp, peeled and deveined",
        "cooked shrimp",
        "shrimp tempura",
        "large shrimp",
        "raw shrimp",
        "korean shrimp paste - saeujeot",
        "mixed seafood",
    ],

    'seafood': [
        "assorted shellfish",
        "anchovies",
        "anchovy fillets packed in olive oil",
        "canned tuna in olive oil",
        "canned tuna",
        "catfish fillets",
        "clam juice",
        "clams",
        "cod fillets",
        "cod",
        "cooked octopus",
        "cooked shrimp",
        "dashi stock",
        "dried anchovies - myulchi",
        "dried bonito flakes (katsuobushi)",
        "fish cake (odeng)",
        "fish sauce",
        "fish stock",
        "fish",
        "fresh clams",
        "grilled chicken or fish (flaked)",
        "haddock fillets",
        "halibut fillet",
        "ikura (salmon roe)",
        "imitation crab meat",
        "korean anchovy broth",
        "korean fish cake broth (dashi)",
        "large shrimp",
        "littleneck clams",
        "lump crab meat",
        "mixed seafood",
        "mussels",
        "narutomaki (fish cake slices)",
        "oyster sauce",
        "salmon fillet",
        "salmon flakes (cooked and flaked)",
        "sashimi-grade salmon",
        "sashimi-grade tuna",
        "scallops - dry packed",
        "sea bass fillets",
        "sea scallops",
        "shrimp - medium",
        "shrimp tempura",
        "shrimp",
        "shrimp, peeled and deveined",
        "sliced kamaboko (fish cake)",
        "tilapia fillets",
        "trout fillets",
        "tuna - sushi grade",
        "tuna (canned in water)",
        "tuna steak",
        "tuna steaks",
        "tuna",
        "white fish fillets",
        "crab",
        "smoked salmon",
        "worcestershire sauce",
        "caesar dressing",
    ],

    'sesame': [
        "furikake seasoning",
        "hummus",
        "irigoma (white sesame seeds)",
        "korean sesame seeds",
        "sesame oil",
        "sesame seeds",
        "shichimi togarashi (japanese seven-spice powder)",
        "tahini sauce",
        "tahini",
        "toasted sesame oil",
        "toasted sesame seeds",
        "white sesame seeds",
    ],

    'sulfite': [
        "sulfite",
        "sulfites",
        "sulphite",
        "sulphites",
        "sulfur dioxide",
        "sulphur dioxide",
    ],

    'wheat': [
        "all-purpose flour",
        "bagel",
        "baguette bread - large",
        "baguette",
        "bread - sourdough",
        "bread - white",
        "bread - whole wheat",
        "bread cubes",
        "bread",
        "breadcrumbs",
        "ciabatta bread",
        "couscous",
        "crackers",
        "cream of wheat",
        "croutons",
        "crushed breadcrumbs",
        "day-old bread",
        "dough",
        "elbow macaroni",
        "english muffins",
        "fettuccine",
        "flour tortilla",
        "flour tortillas - large",
        "flour tortillas",
        "fresh breadcrumbs",
        "french bread",
        "graham cracker crumbs",
        "graham crackers",
        "gyoza wrappers",
        "hamburger buns",
        "hotdog buns",
        "italian seasoned breadcrumbs",
        "jumbo pasta shells",
        "lasagna noodles",
        "linguine",
        "lo mein noodles - dried",
        "lo mein noodles",
        "macaroni",
        "noodles",
        "panko breadcrumbs",
        "pasta (long, such as spaghetti, linguine, or fettuccine)",
        "pasta (such as penne or fusilli)",
        "pasta (such as penne or spaghetti)",
        "pasta",
        "penne pasta",
        "phyllo dough",
        "pie crust",
        "pizza dough",
        "pita bread",
        "puff pastry",
        "ramen noodles",
        "ravioli",
        "rigatoni pasta",
        "round dumpling wrappers",
        "self-rising flour",
        "semolina flour",
        "shreddies",
        "small pasta",
        "spaghetti",
        "tagliatelle",
        "wonton wrappers",
        "yakisoba noodles",
        "ziti pasta",
    ],
}

    user_allergies = []

    for allergy in allergies:
        user_allergies.append(allergy_restrictions[allergy])

    return user_allergies
