import os

import pandas as pd


def get_all_unique_units():
    """
    Get all unique units from the ingredients CSV files and write them to a text file.
    Handles files with an inconsistent number of columns by focusing on the first three.
    """
    all_units = set()
    directory_path = "ingredients_csv"

    for file in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file)
        try:
            # Read only the first three columns and handle any bad lines by warning
            df = pd.read_csv(file_path, usecols=[0, 1, 2], header=None, on_bad_lines='warn')
            # The third column is the 'Unit' column
            all_units.update(df.iloc[:, 2].dropna().unique().tolist())
        except Exception as e:
            print(f"Error processing {file}: {e}")

    with open("all_unique_units.txt", "w") as file:
        for unit in all_units:
            file.write(f"{unit}\n")


def get_all_unique_ingredients():
    """
    Get all unique ingredients from the ingredients CSV files and write them to a text file.
    Handles files with an inconsistent number of columns by focusing on the first column.
    """
    all_ingredients = set()
    directory_path = "ingredients_csv"

    for file in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file)
        try:
            # Read only the first column, assumed to be 'Ingredient', and handle any bad lines by warning
            df = pd.read_csv(file_path, usecols=[0], header=None, on_bad_lines='warn')
            # Assume the first column is the 'Ingredient' column
            all_ingredients.update(df.iloc[:, 0].dropna().unique().tolist())
        except Exception as e:
            print(f"Error processing {file}: {e}")

    with open("all_unique_ingredients.txt", "w") as file:
        for ingredient in all_ingredients:
            file.write(f"{ingredient}\n")


def find_recipe_number_by_unit(unit: str):
    """
    Find and print the recipe numbers that contain the specified unit.
    """
    directory_path = "ingredients_csv"

    file_paths = [os.path.join(directory_path, file) for file in os.listdir(directory_path)]

    for file_path in file_paths:
        try:
            # Read the CSV, focusing on the first three columns
            df = pd.read_csv(file_path, usecols=[0, 1, 2], on_bad_lines='warn')

            # Check if 'Unit' column exists and if the specified unit is in the list of units
            if 'Unit' in df.columns and unit.lower() in df['Unit'].str.lower().tolist():
                file_path_with_extension = os.path.basename(file_path)
                recipe_number = os.path.splitext(file_path_with_extension)[0]
                print(f"Unit {unit} found in recipe #{recipe_number}")
            elif 'Unit' not in df.columns:
                print(f"No 'Unit' column found in file {file_path}")
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")


def find_recipe_number_by_ingredient(ingredient: str):
    """
    Find and print the recipe numbers that contain the specified ingredient.
    """
    directory_path = "ingredients_csv"

    file_paths = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if
                  file.endswith('.csv')]

    for file_path in file_paths:
        try:
            # Read the CSV with more flexibility on the number of columns
            df = pd.read_csv(file_path, on_bad_lines='warn', usecols=[0, 1, 2])
            # Check if the 'Ingredient' column is in the DataFrame to avoid KeyErrors
            if 'Ingredient' in df.columns and ingredient.lower() in df['Ingredient'].str.lower().tolist():
                file_path_with_extension = os.path.basename(file_path)
                recipe_number = os.path.splitext(file_path_with_extension)[0]
                print(f"Ingredient {ingredient} found in recipe #{recipe_number}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")


def delete_recipes_with_ingredients(ingredient_list_path, ingredients_dir, instructions_dir):
    """
    Deletes recipes based on a list of ingredients.

    :param ingredient_list_path: Path to the text file containing ingredients to check.
    :param ingredients_dir: Directory containing ingredients CSV files.
    :param instructions_dir: Directory containing corresponding instructions files.
    """
    # Read ingredients from the text file
    with open(ingredient_list_path, 'r') as file:
        ingredients_to_remove = set(line.strip().lower() for line in file if line.strip())

    # Iterate over each file in the ingredients directory
    for file_name in os.listdir(ingredients_dir):
        if file_name.endswith('.csv'):
            file_path = os.path.join(ingredients_dir, file_name)

            try:
                # Load the CSV file, focusing on processing the 'Ingredient' column
                df = pd.read_csv(file_path, usecols=['Ingredient'], on_bad_lines='warn')
                # Ensure all entries are strings and flatten all ingredients into a single set
                current_ingredients = set(str(ing).lower() for ing in df['Ingredient'].tolist() if pd.notna(ing))

                # Check if any undesirable ingredient is in the current recipe
                if ingredients_to_remove.intersection(current_ingredients):
                    # Match found, delete this file and its corresponding instructions file
                    os.remove(file_path)
                    instructions_file_path = os.path.join(instructions_dir, file_name)
                    if os.path.exists(instructions_file_path):
                        os.remove(instructions_file_path)
                    print(f"Deleted {file_name} and its corresponding instructions file.")
            except Exception as e:
                print(f"Error processing {file_name}: {e}")


def main():
    get_all_unique_units()
    get_all_unique_ingredients()
    find_recipe_number_by_unit("beaten (for egg wash)")
    find_recipe_number_by_ingredient("Beef brisket")

    # Delete all recipes containing certain ingredients
    delete_recipes_with_ingredients('to_delete.txt', 'ingredients_csv',
                                                     'instructions_csv')


if __name__ == "__main__":
    main()
