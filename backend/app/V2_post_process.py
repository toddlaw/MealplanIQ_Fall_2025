import csv
import datetime
import ast
import json
import pandas as pd
from typing import List, Dict
import io


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
    
    response = {}
    response['constraints_loosened'] = optimized_results["constraints_loosened"]
    response['tableData'] = create_table_data(optimized_results)
    
    #print("\n\n RECIPES:\n\n", optimized_results['recipes'])
    recipes = extract_recipes(optimized_results['recipes'])
    #print("\n\nEXTRACTED RECIPES:\n\n", recipes)
    processed_recipe = process_recipes(recipe_df, recipes)
    #print("\n\nprocessed Recipe:\n\n", processed_recipe)
    recipes_balanced_by_day = sort_by_tags(processed_recipe, days)
    #print("\n\nSORTED BY TAGS:\n\n", recipes_balanced_by_day)
    days = create_days_array(recipes_balanced_by_day, min_date, days)
    #print("\n\nDAYS ARRAY:\n\n", days)
    
    response["days"] = days
    
    return response

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

def process_recipes(recipe_df, recipes):
    """
    Returns list of processed recipes by appending information described in process_recipe()
    """
    processed_recipe = []
    for recipe in recipes:
        processed_recipe.append(process_recipe(recipe_df, recipe))
        
    return processed_recipe

def sort_by_tags(processed_recipe, days):
    """
    Sort recipes into groups of 9 based on meal criteria:
    - 1 lunch
    - 1 dinner
    - 2 snacks
    - 2 sides
    - 3 breakfasts if 9 recipes per day
    - 2 breakfasts if 8 recipes per day
    - 1 breakfasts if 7 recipes per day
    """
    num_days = days
    recipes_per_day = int(len(processed_recipe)/num_days)
    #print("\n\n RECIPES PER DAY\n\n:", recipes_per_day)
    
    breakfast_recipes = []
    lunch_recipes = []
    main_recipes = []
    side_recipes = []
    snack_recipes = []
    
    multi_slot_items = []
    single_slot_items = []
    
    # Calculate maximum allowed for each category
    max_lunch = num_days * 1    # 1 per day
    max_main = num_days * 1     # 1 per day
    max_snack = num_days * 2    # 2 per day
    max_side = num_days * 2     # 2 per day 
    max_breakfast = num_days * 3 # 3 per day
    if recipes_per_day == 8:
        max_breakfast = num_days * 2 # 2 per day if 8 recipes per day
    elif recipes_per_day ==7:
        max_breakfast = num_days * 1 # 1 per day if 7 recipes per day
    
    for meal_dict in processed_recipe:
        # Clean up each item by removing brackets, outer quotes, spaces
        meal_slots_str = meal_dict['meal_slot'].strip('"[]').split(',')
        meal_slots = [slot.strip().strip("'") for slot in meal_slots_str]
    
        if len(meal_slots) == 1:
            single_slot_items.append((meal_dict, meal_slots))
        else:
            multi_slot_items.append((meal_dict, meal_slots))


    for meal_dict, meal_slots in single_slot_items:
        
        print("meal_slots in single slot_items", meal_slots)
        raw_slots = meal_dict.get("meal_slot")

            # 문자열이면 파싱
        if isinstance(raw_slots, str):
            try:
                meal_slots = ast.literal_eval(raw_slots)
            except Exception:
                meal_slots = []  # fallback
        else:
            meal_slots = raw_slots

        if 'breakfast' in meal_slots and len(breakfast_recipes) < max_breakfast:
            meal_dict["meal_name"] = "Breakfast"
            breakfast_recipes.append(meal_dict)
        if 'snack' in meal_slots and len(snack_recipes) < max_snack:
            meal_dict["meal_name"] = "Snack"
            snack_recipes.append(meal_dict)
        elif 'lunch' in meal_slots and len(lunch_recipes) < max_lunch:
            meal_dict["meal_name"] = "Lunch "
            lunch_recipes.append(meal_dict)
        elif 'main' in meal_slots and len(main_recipes) < max_main:
            meal_dict["meal_name"] = "Main"
            main_recipes.append(meal_dict)
        elif 'snack' in meal_slots and len(snack_recipes) < max_snack:
            meal_dict["meal_name"] = "Snack"
            snack_recipes.append(meal_dict)
        elif 'side' in meal_slots and len(side_recipes) < max_side:
            meal_dict["meal_name"] = "Side"
            side_recipes.append(meal_dict)


    for meal_dict, meal_slots in multi_slot_items:
        print("meal_slots in multi_slot_items", meal_slots)
        placed = False


        if 'lunch' in meal_slots and len(lunch_recipes) < max_lunch:
            meal_dict["meal_name"] = "Lunch"
            lunch_recipes.append(meal_dict)
            placed = True

        if 'breakfast' in meal_slots and len(breakfast_recipes) < max_breakfast:
            meal_dict["meal_name"] = "Breakfast"
            breakfast_recipes.append(meal_dict)
            placed = True

        elif 'main' in meal_slots and len(main_recipes) < max_main:
            meal_dict["meal_name"] = "Main"
            main_recipes.append(meal_dict)
            placed = True

        elif 'snack' in meal_slots and len(snack_recipes) < max_snack:
            meal_dict["meal_name"] = "Snack"
            snack_recipes.append(meal_dict)

        elif 'side' in meal_slots and len(side_recipes) < max_side:
            meal_dict["meal_name"] = "Side"
            side_recipes.append(meal_dict)
            placed = True

        if not placed:
            meal_dict["meal_name"] = "Snack"
            snack_recipes.append(meal_dict)

    result_groups = []
    for i in range(int(num_days)):
        current_group = []
        if recipes_per_day == 9:
        # Add 3 breakfasts
            current_group.extend(breakfast_recipes[i*3:i*3+3])
        elif recipes_per_day == 8:
            current_group.extend(breakfast_recipes[i*2:i*2+2])
        elif recipes_per_day == 7:
            current_group.extend(breakfast_recipes[i*1:i*1+1])
        # Add first snack
        current_group.append(snack_recipes[i*2])
        # Add lunch
        current_group.append(lunch_recipes[i])
        # Add second snack
        current_group.append(snack_recipes[i*2+1])
        # Add main (dinner)
        current_group.append(main_recipes[i])
        # Add 2 sides
        current_group.extend(side_recipes[i*2:i*2+2])
        # Adds current_group (a singular day) to the list of days ("days" don't exist yet - added in create_days_aray)
        result_groups.append(current_group)

    return result_groups


def create_days_array(recipes_balanced_by_day, min_date, days):
    base = min_date
    date_list = [base + datetime.timedelta(days=x) for x in range(days)]
    days_array = []

    for i, date in enumerate(date_list):
        day = date.strftime("%Y-%m-%d")
        # Now we take the entire sublist for each day, no slicing needed
        days_array.append(create_meal_date(recipes_balanced_by_day[i], day))
    
    return days_array

    

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
    --------
    @author: BCIT May 2025
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

    with open(instruction_file_path, newline='', encoding='utf-8', errors='replace') as csvfile:
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

    for key, value in recipe_dict.items():
        res[key] = f"{value}"

    # Convert ingredients from a string to a list
    res['ingredients'] = ast.literal_eval(res['ingredients'])
    res['instructions'] = ast.literal_eval(res['instructions'])
    res['ingredients_with_quantities'] = ast.literal_eval(
        res['ingredients_with_quantities'])

    return res