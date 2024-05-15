import os

import pandas as pd


class DataCleanser:
    """
    This class contains methods to clean the data in the ingredients CSV files.
    """
    @classmethod
    def get_all_unique_units(cls):
        """
        Get all unique units from the ingredients CSV files and write them to a text file.
        """
        all_units = set()

        directory_path = "../new_meal_db_creation/ingredients_csv"

        for file in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file)
            df = pd.read_csv(file_path)
            all_units.update(df["Unit"].tolist())

        with open("all_unique_units.txt", "w") as file:
            for unit in all_units:
                file.write(f"{unit}\n")

    @classmethod
    def find_recipe_number_by_unit(cls, unit: str):
        """
        Find and print the recipe numbers that contain the specified unit.
        """
        directory_path = "../new_meal_db_creation/ingredients_csv/"

        file_paths = [os.path.join(directory_path, file) for file in os.listdir(directory_path)]

        for file_path in file_paths:
            df = pd.read_csv(file_path)

            if unit in df["Unit"].tolist():
                file_path_with_extension = os.path.basename(file_path)
                recipe_number = os.path.splitext(file_path_with_extension)[0]
                print(f"Unit {unit} found in recipe #{recipe_number}")

    @classmethod
    def find_recipe_number_by_ingredient(cls, ingredient: str):
        """
        Find and print the recipe numbers that contain the specified ingredient.
        """
        directory_path = "../new_meal_db_creation/ingredients_csv/"

        file_paths = [os.path.join(directory_path, file) for file in os.listdir(directory_path)]

        for file_path in file_paths:
            df = pd.read_csv(file_path)

            if ingredient in df["Ingredients"].tolist():
                file_path_with_extension = os.path.basename(file_path)
                recipe_number = os.path.splitext(file_path_with_extension)[0]
                print(f"Ingredient {ingredient} found in recipe #{recipe_number}")
