import csv
import datetime
import ast
import json
import pandas as pd

from app.mealplan_service import read_recipe_assets_from_gcs


# add optimized_snacks as input
def post_process_results(recipe_df, optimized_results, optimized_snacks, min_date, days):
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
    print("===============")
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
        print("\n\nOPTIMIZED RESULTS BEFORE REDUCED: \n\n",optimized_results)
        
        print(f'\n\nMEALS BY CALORIES:\n{meals_by_calories},\n\nNUM_MULTIPLES:\n {num_multiples},\n\nDAYS:\n {days}\n\n')
        #optimized_results = reduce_optimized_results(         # modify: reduce_optimized_results doesn't return optimized_snacks
        #    meals_by_calories, num_multiples, optimized_results, days)
        print("\n\nOPTIMIZED RESULTS AFTER REDUCED: \n\n",optimized_results)
        days = create_days_array(recipe_df, optimized_results, min_date, days)
        print("\n\nDAYS IN OPTIMIZEATION: \n\n",days)
        # print("24optimized_snacks", optimized_snacks)
        response['days'] = days
        response['snacks'] = create_snacks_array(recipe_df, optimized_snacks)
    # print("optimized_snacks_hh", optimized_snacks)
    # print("optimized_results_hh", optimized_results)
    # print("4444444:", response['snacks'])
    print("===============")

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
            optimized_results = reduce_results(
                # modify: take optimized_snacks away from the input
                optimized_results, lowest_cal_recipe_name)
            num_multiples_of_lowest_cal_recipe -= 1
            current_multiples = get_total_multiples(optimized_results)
    print("optimized snacks", optimized_snacks)
    print("optimized_results_hhh", optimized_results)

    return optimized_results                   # modify: don't return optimized_snacks


def get_multiples_for_recipe(optimized_results, recipe_name):
    """
    Given a recipe name, returns the number of multiples of that recipe
    in the optimized_results dictionary.
    """
    for recipe in optimized_results['recipes']:
        if recipe['name'] == recipe_name:
            return recipe['multiples']

    return 0


# modify: take optimized_snacks away from the input
def reduce_results(optimized_results, recipe_name):
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
            # optimized_snacks = add_multiple_to_snacks(optimized_snacks,           #  delete: don't modify optimized_snacks
            #                                           recipe_name)

            break

    return optimized_results    # modify: on't return optimized_snacks


# def add_multiple_to_snacks(optimized_snacks, recipe_name):   # won't be called
#     """
#     Given a recipe name, adds a multiple of that recipe to the optimized_snacks
#     array. If the recipe is already in the array, then it just adds a multiple
#     to that recipe.
#     """
#     for snack in optimized_snacks:
#         if snack['name'] == recipe_name:
#             snack['multiples'] += 1
#             return optimized_snacks

#     # if the recipe is not in the optimized_snacks array, then add it
#     optimized_snacks.append({'name': recipe_name, 'multiples': 1})

#     return optimized_snacks


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
    print("Days: ------------ ", days)
    recipes = extract_recipes(optimized_results['recipes'])
    print("\n\nextracted recipes\n\n", recipes)
    recpies_balanced_by_day = balance_recipe_calories(recipe_df, recipes)
    print("\n\nrecpies_balanced_by_day\n\n", recpies_balanced_by_day)
    # includes nutritional info and recipe infomration for all recipes (all the 9)
    base = min_date
    date_list = [base + datetime.timedelta(days=x) for x in range(days)]
    start_slice_index = 0
    start_slice_end = 9
    index_increment = 9
    days_array = []

    for date in date_list:
        day = date.strftime("%Y-%m-%d")
        # print("what", recpies_balanced_by_day[
        # start_slice_index:start_slice_end])
        days_array.append(create_meal_date(recpies_balanced_by_day[
            start_slice_index:start_slice_end],
            day))
        
        start_slice_index += index_increment
        start_slice_end += index_increment

    print("\n\ndays array before reverse\n\n", days_array)
    # sort the days_array by date descending by just reversing the array
    days_array.reverse()
    print("\n\ndays array after reverse\n\n", days_array)
    return days_array


def balance_recipe_calories(recipe_df, recipes):
    """
    takes recipes and balances them by calories. The goal is to reduce the
    disparity of calories between the days.
    """
    column_headers_sus1 = list(recipe_df.columns.values)
    processed_recipe = []
    for recipe in recipes:
        processed_recipe.append(process_recipe(recipe_df, recipe))
        
        
    
    #returned_recipes = sort_by_tags(processed_recipe)    
        

    print("\n\nprocessed Recipe:\n\n", processed_recipe)
    
    
    # sort based off of Calories
    processed_recipe = sorted(
        processed_recipe, key=lambda x: float(x['calories']))

    return processed_recipe
    # split into 3 lists
    # list_length = len(processed_recipe)
    # low_cal = processed_recipe[:list_length//3]
    # low_cal.reverse()
    # mid_cal = processed_recipe[list_length//3:2*list_length//3]
    # high_cal = processed_recipe[2*list_length//3:]
    # high_cal.reverse()

    # returned_recipes = []
    # while len(low_cal) > 0:
    #     returned_recipes.append(low_cal.pop(0))
    #     returned_recipes.append(mid_cal.pop(0))
    #     returned_recipes.append(high_cal.pop(0))
    # return returned_recipes

def sort_by_tags(recipes):
    
    def parse_meal_slots(meal_slot_str):
        return eval(meal_slot_str.strip('"'))
    
    def sort_single_day(day_recipes):
        breakfasts = []
        lunches = []
        mains = []
        sides = []
        others = []
        
        for recipe in day_recipes:
            meal_slots = parse_meal_slots(recipe['meal_slot'])
            if len(meal_slots) ==1:
                if 'breakfast' in meal_slots:
                    breakfasts.append(recipe)
                elif 'lunch' in meal_slots:
                    lunches.append(recipe)
                elif 'main' in meal_slots:
                    mains.append(recipe)
                elif 'side' in meal_slots:
                    sides.append(recipe)
                else:
                    others.append(recipe)
        
        sorted_day = []
        
        sorted_day.extend(breakfasts)
        
        sorted_day.append(lunches.pop(0))
        
        sorted_day.append(mains.pop(0))
        
        sorted_day.extend(sides)
        
        sorted_day.extend(lunches)
        sorted_day.extend(mains)
        sorted_day.extend(others)
        
        return sorted_day
    
    num_days = len(recipes) // 9
    sorted_recipes = []
    
    for day in range(num_days):
        start_idx = day * 9
        end_idx = start_idx + 9
        day_recipes = recipes[start_idx:end_idx]
        
        sorted_day = sort_single_day(day_recipes)
        sorted_recipes.extend(sorted_day)
    
    return sorted_recipes

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

    # retrive instructions

    instruction_file_path = f'''./meal_db/instructions/instructions_{
        recipe_dict['id']}.csv'''
    ingredient_file_path = f"./meal_db/ingredients/{recipe_dict['id']}.csv"

    # instruction_content = pd.read_csv(instruction_file_path)
    # recipe_dict['instructions'] = instruction_content.values.tolist()

    with open(instruction_file_path, newline='') as csvfile:
        content = csv.reader(csvfile)
        recipe_dict['instructions'] = []
        for row in content:
            recipe_dict['instructions'].append(row)

    # retrive ingredients_with_quantities

    # cannot use pandas here, will raise an error

    with open(ingredient_file_path, newline='') as csvfile:
        content = csv.reader(csvfile)
        recipe_dict['ingredients_with_quantities'] = []
        for row in content:
            recipe_dict['ingredients_with_quantities'].append(row)

    #
     # retrive instructions from bucket => make sure to use this for production stage
#     instructions, ingredients = read_recipe_assets_from_gcs(
#     str(recipe_dict["id"]),
#     bucket_name="meal-plan-data",         
#     base_prefix="meal_db"                 
# )

#     recipe_dict['instructions'] = instructions
#     recipe_dict['ingredients_with_quantities'] = ingredients        

    for key, value in recipe_dict.items():
        res[key] = f"{value}"

    # Convert ingredients from a string to a list
    res['ingredients'] = ast.literal_eval(res['ingredients'])
    res['instructions'] = ast.literal_eval(res['instructions'])
    res['ingredients_with_quantities'] = ast.literal_eval(
        res['ingredients_with_quantities'])

    return res
