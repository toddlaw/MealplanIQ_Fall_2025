import datetime
import ast


def post_process_results(recipe_df, optimized_results, min_date, days):
    """
    Called to process the results from the optimization function in addition
    to other data so that a JSON response can be sent to the frontend.

    recipe_df: pandas dataframe of recipes
    optimized_results: dictionary of results from the optimization function
    form of
    {
        'recipes': [ {'name': 'recipe_name', 'multiples': 2}, ... ],
        'status': 'Optimal',
        'constraint_targets': [{'nutrientName': 'calories', 'actual': 2000, 'target': 2000 - 3000}, ...]
    }

    """
    meals_by_calories = []
    optimized_snacks = []
    num_multiples = get_total_multiples(optimized_results)
    response = {}

    response['constraints_loosened'] = optimized_results["constraints_loosened"]

    if num_multiples <= days * 3:
        days = create_days_array(recipe_df, optimized_results, min_date, days)
        response['days'] = days
        response['snacks'] = optimized_snacks
        response['tableData'] = create_table_data(optimized_results)
    elif num_multiples > days * 3:
        response['tableData'] = create_table_data(optimized_results)
        meals_by_calories = get_meals_by_calories(recipe_df, optimized_results)
        optimized_results, optimized_snacks = reduce_optimized_results(
            meals_by_calories, num_multiples, optimized_results, days)
        days = create_days_array(recipe_df, optimized_results, min_date, days)
        response['days'] = days
        response['snacks'] = create_snacks_array(recipe_df, optimized_snacks)

    return response


def create_snacks_array(recipe_df, optimized_snacks):
    """
    Given a pandas dataframe of recipes and an array of recipe dictionaries
    that contain the name of the recipe and the number of multiples of that
    recipe, creates an array of dictionaries that contain all of the information
    for the recipes that the frontend expects
    """
    snacks_array = []
    for snack in optimized_snacks:
        recipe = process_recipe(recipe_df, snack['name'])
        recipe['multiples'] = snack['multiples']
        snacks_array.append(recipe)

    return snacks_array


def get_meals_by_calories(recipe_df, optimized_results):
    meals_by_calories = []
    for recipe in optimized_results['recipes']:
        meals_by_calories.append(process_recipe(recipe_df, recipe['name']))

    # sort the meals_by_calories by calories
    return sorted(meals_by_calories, key=lambda x: float(x['calories']),
                  reverse=True)


def reduce_optimized_results(meals_by_calories, num_multiples,
                             optimized_results, days):
    """
    Reduces the number of multiples in the optimized_results dictionary by taking
    away the lowest calorie recipe until the number of multiples is = days * 3.
    It adds those taken away recipes to th optimized_snacks array.
    """
    # meals_by_calories is sorted by greatest calories to least calories
    target_multiples = days * 3
    optimized_snacks = []
    current_multiples = num_multiples  # 37 for example

    while current_multiples > target_multiples:
        lowest_cal_recipe = meals_by_calories.pop()
        lowest_cal_recipe_name = lowest_cal_recipe['title']
        num_multiples_of_lowest_cal_recipe = get_multiples_for_recipe(
            optimized_results, lowest_cal_recipe_name)
        while num_multiples_of_lowest_cal_recipe > 0 and current_multiples > target_multiples:
            optimized_results, optimized_snacks = reduce_optmized_results(
                optimized_results, optimized_snacks, lowest_cal_recipe_name)
            num_multiples_of_lowest_cal_recipe -= 1
            current_multiples = get_total_multiples(optimized_results)

    return optimized_results, optimized_snacks


def get_multiples_for_recipe(optimized_results, recipe_name):
    """
    Given a recipe name, returns the number of multiples of that recipe
    in the optimized_results dictionary.
    """
    for recipe in optimized_results['recipes']:
        if recipe['name'] == recipe_name:
            return recipe['multiples']

    return 0


def reduce_optmized_results(optimized_results, optimized_snacks, recipe_name):
    """
    Given a recipe name, reduces the multiples of that recipe in the
    optimized_results dictionary by 1. If the multiples of that recipe
    are 0, then the recipe is removed from the dictionary.

    Also adds the removed recipe to the optimized_snacks array.
    """

    for recipe in optimized_results['recipes']:
        if recipe['name'] == recipe_name:
            recipe['multiples'] -= 1
            if recipe['multiples'] == 0:
                optimized_results['recipes'].remove(recipe)
            optimized_snacks = add_multiple_to_snacks(optimized_snacks,
                                                     recipe_name)

            break

    return optimized_results, optimized_snacks


def add_multiple_to_snacks(optimized_snacks, recipe_name):
    """
    Given a recipe name, adds a multiple of that recipe to the optimized_snacks
    array. If the recipe is already in the array, then it just adds a multiple
    to that recipe.
    """
    for snack in optimized_snacks:
        if snack['name'] == recipe_name:
            snack['multiples'] += 1
            return optimized_snacks

    # if the recipe is not in the optimized_snacks array, then add it
    optimized_snacks.append({'name': recipe_name, 'multiples': 1})

    return optimized_snacks


def get_total_multiples(optimized_results):
    total_multiples = 0
    for recipe in optimized_results['recipes']:
        total_multiples += recipe['multiples']
    return total_multiples


def create_table_data(optimized_results):
    """

    """
    table_data = []
    for constraint in optimized_results["constraint_targets"]:
        entry = {}
        entry["nutrientName"] = constraint["name"]
        entry["actual"] = constraint["actual"]
        entry["target"] = constraint["target"]
        table_data.append(entry)

    return table_data


def find_similair_key_in_dict(dict, key_name):
    result = ""
    for key in dict.keys():
        if key_name.lower() in key.lower():
            result = key
            break
    return result


def extract_recipes(array_of_recipe_dict):
    """
    Given an array of recipe dictionaries, creates multiple entries for any with
    multiples > 1. the recipe dict is in the form
    {
        'name': 'recipe_name',
        'multiples': 2
    }

    returns an array with the recipe name
    """
    recipes = []
    for recipe in array_of_recipe_dict:
        while recipe['multiples'] > 0:
            recipes.append(recipe['name'])
            recipe['multiples'] -= 1

    return recipes


def create_days_array(recipe_df, optimized_results, min_date, days):
    # this list below only includes the recipe names
    print("Days: ", days)
    recipes = extract_recipes(optimized_results['recipes'])
    recpies_balanced_by_day = balance_recipe_calories(recipe_df, recipes)
    base = min_date
    date_list = [base + datetime.timedelta(days=x) for x in range(days)]
    start_slice_index = 0
    start_slice_end = 3
    index_increment = 3
    days_array = []

    for date in date_list:
        day = date.strftime("%Y-%m-%d")
        days_array.append(create_meal_date(recpies_balanced_by_day[
                                                      start_slice_index:start_slice_end],
                                           day))
        start_slice_index += index_increment
        start_slice_end += index_increment

    #sort the days_array by date descending by just reversing the array
    days_array.reverse()

    return days_array


def balance_recipe_calories(recipe_df, recipes):
    """
    takes recipes and balances them by calories. The goal is to reduce the
    disparity of calories between the days.
    """
    processed_recipe = []
    for recipe in recipes:
        processed_recipe.append(process_recipe(recipe_df, recipe))

    # sort based off of Calories
    processed_recipe = sorted(processed_recipe, key=lambda x: float(x['calories']))

    # split into 3 lists
    list_length = len(processed_recipe)
    low_cal = processed_recipe[:list_length//3]
    low_cal.reverse()
    mid_cal = processed_recipe[list_length//3:2*list_length//3]
    high_cal = processed_recipe[2*list_length//3:]
    high_cal.reverse()

    returned_recipes = []
    while len(low_cal) > 0:
        returned_recipes.append(low_cal.pop(0))
        returned_recipes.append(mid_cal.pop(0))
        returned_recipes.append(high_cal.pop(0))

    return returned_recipes


def create_meal_date(recipes, day):
    """
    Given a recipe and a day of the week, creates a dictionary that contains
    all of the information for the recipe that the frontend expects
    """
    day_dict = {}

    date_object = datetime.datetime.strptime(day, '%Y-%m-%d')
    day_dict['date'] = day
    day_dict['date_weekday'] = date_object.strftime('%A %B %d')
    recipe_array = []

    for recipe in recipes:
        recipe_array.append(recipe)

    day_dict['recipes'] = recipe_array

    return day_dict


def process_recipe(recipe_df, recipe_name):
    """
    Given a pandas dataframe of recipes creates a dictionary that contains
    all of the information for the recipe with the given name that the frontend
    expects
    """
    recipe_row = recipe_df.loc[recipe_df['title'] == recipe_name]
    res = {}
    recipe_dict = {}
    recipe_dict['carbohydrates'] = recipe_row['carbohydrates_g'].values[0]
    recipe_dict['country'] = recipe_row['country'].values[0]
    recipe_dict['fat'] = recipe_row['fats_total_g'].values[0]
    recipe_dict['price'] = "N/A"
    recipe_dict['protein'] = recipe_row['protein_g'].values[0]
    recipe_dict['region'] = recipe_row['region'].values[0]
    recipe_dict['title'] = recipe_row['title'].values[0]
    recipe_dict['ingredients'] = recipe_row['ingredients'].values[0]
    recipe_dict['calories'] = recipe_row['energy_kcal'].values[0]
    recipe_dict['meal_slot'] = recipe_row['meal_slot'].values[0]
    recipe_dict['id'] = recipe_row['number'].values[0]
    recipe_dict['cook_time'] = recipe_row['cooktime'].values[0]
    recipe_dict['prep_time'] = recipe_row['preptime'].values[0]
    recipe_dict['sub_region'] = recipe_row['subregion'].values[0]

    for key, value in recipe_dict.items():
        res[key] = f"{value}"

    # Convert ingredients from a string to a list
    res['ingredients'] = ast.literal_eval(res['ingredients'])

    return res
