import json
import os

from rapidfuzz import process, fuzz

import pandas as pd
import csv


def preprocess_and_read_csv(file_path: str):
    """
    Preprocess the CSV file to ensure that each row has the same number of fields as the headers.

    :param file_path: The path to the CSV file
    :precondition: The file_path is a valid path to a CSV file
    :postcondition: The CSV file will be preprocessed to ensure each row has the same number of fields as the headers
    :return: A DataFrame representing the CSV file
    """
    processed_rows = []
    with open(file_path, 'r', newline='') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Read the headers
        # Define extended headers based on the possibility of an extra field
        extended_headers = headers if len(headers) > 3 else headers + ['Additional Info']

        for row in reader:
            # Check if the current row has more fields than expected
            if len(row) > len(headers):
                row = row[:len(headers)] + [', '.join(row[len(headers):])]  # Assume extra data belongs in the last new column
            # Ensure the row matches the expected number of extended headers
            while len(row) < len(extended_headers):
                row.append(None)  # Append None for missing fields
            processed_rows.append(row)

        df = pd.DataFrame(processed_rows, columns=extended_headers)
        df.columns = [col.strip('\ufeff') for col in df.columns]  # Remove BOM or other hidden characters
        # print("DataFrame Columns:", df.columns)  # Print column names to debug
        return df


def insert_row_values(ingredient_file_path: str, nutrition_file: str, db_row: dict):
    """
    Add values to db_row dictionary keys, which will be the field values corresponding to each column in the database.

    :param ingredient_file_path: The path to the ingredient CSV file
    :param nutrition_file: The path to the nutrition Excel file
    :param db_row: The dictionary representing a row in the database, and keys representing columns
    :precondition: The ingredient_file_path is a valid path to a CSV file
    :precondition: The nutrition_file is a valid path to an Excel file
    :precondition: The db_row is a dictionary with keys corresponding to the columns in the database
    :postcondition: The db_row dictionary will have values added to its keys
    :return: The updated db_row dictionary
    """
    # Add number, tags, and title
    add_number_tag_title('recipe_map.json', db_row, ingredient_file_path)

    # Some rows in the ingredient files may have more fields than columns
    # Preprocess the CSV file to prevent errors
    df = preprocess_and_read_csv(ingredient_file_path)
    for index, row in df.iterrows():  # Iterate through each ingredient row
        ingredient = row['Ingredient']
        quantity = row['Quantity']
        unit = row['Unit']

        db_row['ingredients'] += [ingredient]  # Add the ingredient to the list of ingredients

        add_ingredient_nutrition_values(ingredient, quantity, unit, nutrition_file, db_row)

    # add instructions
    instructions_file = ingredient_file_path.replace('ingredients_csv', 'instructions_csv')
    add_instructions(instructions_file, db_row)
    print(db_row)

    return db_row


def add_number_tag_title(json_file_path, recipe_row, ingredient_file_path):
    """
    Add the recipe number, tags, and title to the recipe_row dictionary based on a JSON file.

    :param json_file_path: A string representing the path to the JSON file
    :param recipe_row: A dictionary representing a row in the database
    :param ingredient_file_path: A string representing the path to the ingredient CSV file
    :precondition: The json_file_path is a valid path to a JSON file
    :precondition: The recipe_row is a dictionary with keys corresponding to the columns in the database
    :precondition: The ingredient_file_path is a valid path to a CSV file
    :postcondition: The recipe_row dictionary will have values added to its keys
    """
    recipe_number = os.path.basename(ingredient_file_path).split('_')[0].replace('.csv', '')
    recipe_row['number'] = recipe_number

    with open(json_file_path) as json_file:
        recipe_map = json.load(json_file)

        recipe_row['tags'] = recipe_map[recipe_number]['tags']
        recipe_row['title'] = recipe_map[recipe_number]['generated name']


def add_nutrient_columns_from_json(json_file_path: str, nutrient_map: dict):
    """
    Add nutrient columns to the nutrient_map dictionary based on a JSON file.

    :param json_file_path: A string representing the path to the JSON file
    :param nutrient_map: A dictionary representing the nutrient values for a recipe
    :precondition: The json_file_path is a valid path to a JSON file
    :precondition: The nutrient_map is a dictionary with keys representing nutrition columns
    """
    with open(json_file_path) as json_file:
        columns_map = json.load(json_file)

        for key in columns_map:
            nutrient_map[key] = 0


def get_general_unit_list():
    """
    Get a dictionary of general units and their corresponding grams.
    """
    with open('grams_general_unit_conversions.json') as json_file:
        general_units = json.load(json_file)
    return general_units


def get_ingredient_grams(ingredient: str, quantity: str, unit: str):
    """
    Get the grams of an ingredient based on the quantity and unit.

    :param ingredient: A string representing the ingredient
    :param quantity: A string representing the quantity of the ingredient
    :param unit: A string representing the unit of the quantity
    :postcondition: The grams of the ingredient will be calculated based on the quantity and unit
    :return: A float representing the grams of the ingredient
    """
    # Get the general unit list
    general_units = get_general_unit_list()
    ingredient_grams = 0

    # Some values in the quantity column are not numbers - e.g., "to taste"
    try:
        quantity = float(quantity)
    except ValueError:
        print(f"Quantity {quantity} is not a number.")
        return 0

    # If the unit already in grams, then return the quantity (which is the grams amount)
    if unit in ['gram', 'grams']:
        ingredient_grams = quantity
    # Some ingredients like "orange" have an average weight in grams taken from the USDA database
    elif ingredient_has_average_grams(ingredient) and unit not in general_units:
        ingredient_grams = ingredient_has_average_grams(ingredient) * quantity
    # Otherwise, convert the unit to grams using the general_units dictionary
    elif unit in general_units:
        ingredient_grams = quantity * general_units[unit]

    print(f"{quantity} {unit} of {ingredient} is {ingredient_grams} grams.")
    return ingredient_grams


def add_ingredient_nutrition_values(ingredient: str, quantity: str, unit: str,
                                    nutrition_file: str, total_nutrients: dict):
    """
    Add the nutrition values for a specific ingredient to the total_nutrients dictionary.

    :param ingredient: A string representing the ingredient
    :param quantity: A string representing the quantity of the ingredient
    :param unit: A string representing the unit of the quantity
    :param nutrition_file: A string representing the path to the nutrition Excel file
    :param total_nutrients: A dictionary representing the total nutrition values for a recipe
    :precondition: nutrition_file is a valid path to an Excel file
    :precondition: total_nutrients is a dictionary with keys representing nutrition columns
    :postcondition: The total_nutrients dictionary will have values added to its keys
    """
    df = pd.read_excel(nutrition_file, header=1)

    # Get the grams of the ingredient based on the quantity and unit
    ingredient_grams = get_ingredient_grams(ingredient, quantity, unit)
    if not ingredient_grams:  # If the quantity is something like "to taste", then skip this ingredient look up
        return

    best_match = find_best_match(df, ingredient, 'Main food description', threshold=70)
    if best_match:
        print(f"Best match: {best_match[0]} with a score of {best_match[1]}")  # Debugging
        matched_row = df[df['Main food description'] == best_match[0]]

        PER_100_GRAMS = 100  # The nutrition values are per 100 grams
        for column in matched_row:  # Iterate through each column in the matched row
            if column in total_nutrients:  # Skip columns like "Food code" that are not nutrition values
                nutrient_value_per_100g = matched_row[column].values[0]
                nutrient_value_for_ingredient_grams = (nutrient_value_per_100g * ingredient_grams) / PER_100_GRAMS
                total_nutrients[column] += round(nutrient_value_for_ingredient_grams, 3)
    # If the ingredient is not matched in the nutrition database, it is skipped
    else:
        print("No close matches found.")


def ingredient_has_average_grams(ingredient: str):
    """
    Retrieve the average grams of an ingredient from a JSON file.

    :param ingredient: A string representing the ingredient
    :precondition: The ingredient is a string
    :postcondition: The average grams of the ingredient will be returned if it exists in the JSON file
    :return: A float representing the average grams of the ingredient, or 0 if the ingredient is not found
    """
    with open('grams_ingredient_conversions.json') as json_file:
        ingredient_grams = json.load(json_file)

        if ingredient in ingredient_grams:
            return ingredient_grams[ingredient]
        else:
            return 0


def find_best_match(df, query, column, threshold=90):
    """
    Finds the best matching string from a specified column in a pandas DataFrame using fuzzy string matching.

    This function uses the `rapidfuzz` library's `process.extractOne` method to find the highest scoring string match
    against a given query. The matching process ranks potential matches using the `token_sort_ratio` scorer, which
    compares token sets after sorting them alphabetically, allowing flexible matching regardless of word order.

    :param df: A pandas DataFrame containing the data to search
    :param query: A string representing the query to match against the DataFrame
    :param column: A string representing the column in the DataFrame to search for matches
    :param threshold: An integer representing the minimum score required for a match
    :precondition: The DataFrame must contain the specified column
    :precondition: The query must be a string
    :precondition: The column must be a string representing a column in the DataFrame
    :precondition: The threshold must be an integer between 0 and 100
    :postcondition: The best matching string will be returned if the score is above the threshold
    :return: A tuple containing the best matching string and its score if the score is above the threshold,
    otherwise None
    """
    choices = df[column].tolist()
    best_match = process.extractOne(query, choices, scorer=fuzz.token_sort_ratio, score_cutoff=threshold)
    return best_match


def add_header_to_csv(file_name: str):
    recipe_row = {
        "number": "",
        "meal_type": "recipe",
        "meal_slot": "",
        "tags": "",
        "title": "",
        "ingredients": [],
        "instructions": {}
    }
    # Assuming this function modifies recipe_row to add more keys based on a JSON map
    add_nutrient_columns_from_json('columns_map.json', recipe_row)

    # Convert dict_keys to a list before creating DataFrame
    columns_list = list(recipe_row.keys())  # Convert the keys to a list explicitly

    # Create an empty DataFrame with these headers
    df = pd.DataFrame(columns=columns_list)

    # Save the DataFrame to CSV with the initial headers
    df.to_csv(file_name, index=False)


def add_instructions(ingredient_file_path: str, recipe_row: dict):
    """
    Add instructions to the recipe_row dictionary.

    :param ingredient_file_path: A string representing the path to the ingredient CSV file
    :param recipe_row: A dictionary representing a row in the database
    :precondition: The ingredient_file_path is a valid path to a CSV file
    :precondition: The recipe_row is a dictionary with keys corresponding to the columns in the database
    :postcondition: The recipe_row dictionary will have instructions added to its keys
    """
    with open(ingredient_file_path, 'r', encoding='ISO-8859-1') as file:
        print(f"Reading instructions from {ingredient_file_path}")
        lines = file.readlines()

        # skip the first line which is the header
        for line in lines[1:]:
            step_and_instruction = line.split(',')
            step = step_and_instruction[0]
            instruction = step_and_instruction[1].strip()
            recipe_row['instructions'][step] = instruction


def create_row() -> dict:
    """
    Create a dictionary representing a row in the database.

    :return: A dictionary representing a row in the database
    """
    row = {
        "number": "",
        "meal_type": "recipe",
        "meal_slot": "",
        "tags": "",
        "title": "",
        "ingredients": [],
        "instructions": {}
    }
    add_nutrient_columns_from_json('columns_map.json', row)
    return row


def add_row_to_db(db_path: str, row: dict):
    """
    Add a row to a CSV file.

    :param db_path: A string representing the path to the CSV file
    :param row: A dictionary representing the row to add to the CSV file
    :precondition: The db_path is a valid path to a CSV file
    :precondition: The row is a dictionary with keys corresponding to the columns in the CSV file
    :postcondition: The row will be added to the CSV file
    """
    try:
        # Load the existing DataFrame
        df = pd.read_csv(db_path)

        # Convert the row dictionary to a DataFrame and ensure it's a single row DataFrame
        row_df = pd.DataFrame([row])

        # Use pd.concat to append the row DataFrame to the existing DataFrame
        df = pd.concat([df, row_df], ignore_index=True)

        # Save the updated DataFrame back to the CSV
        df.to_csv(db_path, index=False)
        print(f"Row successfully added to {db_path}\n")
    except FileNotFoundError:
        print(f"File {db_path} not found.")
    except Exception as e:
        print(f"An error has occurred: {e}")


def main():
    nutrition_file = '2019-2020 FNDDS At A Glance - FNDDS Nutrient Values.xlsx'
    ingredients_directory = 'ingredients_csv'

    new_db_file = 'new_meal_database.csv'

    # Uncomment if the file does not exist, otherwise it will overwrite the existing file
    # add_header_to_csv(new_db_file)

    ingredients_files = os.listdir(ingredients_directory)
    ingredients_files.sort()

    # Creates a dictionary with the keys as the columns in the database. This will represent a row in the database
    db_row = create_row()

    # You can start from a specific nth file in the directory
    # E.g. ingredients_files[450:] will start from the 450th file in the ingredients_csv directory
    for file in ingredients_files[28:]:
        if file == '.DS_Store':
            continue

        ingredient_file = os.path.join(ingredients_directory, file)
        insert_row_values(ingredient_file, nutrition_file, db_row)
        add_row_to_db(new_db_file, db_row)  # Add the row to the database csv file
        db_row = create_row()  # Reset the row for the next iteration


if __name__ == '__main__':
    main()
