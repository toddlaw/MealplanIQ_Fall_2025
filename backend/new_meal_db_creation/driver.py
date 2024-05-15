from backend.new_meal_db_creation.data_cleanser import DataCleanser
from backend.new_meal_db_creation.openai_meal_generator import *


def main():
    recipe_details = retrieve_recipe_details("new_recipes.xlsx")

    # start_number = 200800 # Change this to the recipe number you want to start from
    #
    # # Find the index of the start number
    # start_index = recipe_details["Number"].index(start_number)
    #
    # # Otherwise, use this for the for loop range
    # rows = len(recipe_details["Number"])
    #
    # for i in range(start_index, rows):
    #     dish_type = recipe_details["Informal Name"][i]
    #     dish_name = recipe_details["Generated Name"][i]
    #     number = int(recipe_details["Number"][i])
    #
    #     recipe_details_dict = generate_ingredients_and_instructions(dish_type, dish_name, number)
    #     create_csv_file(recipe_details_dict, number)

    DataCleanser.get_all_unique_units()
    # DataCleanser.find_recipe_number_by_unit("30")
    # DataCleanser.find_recipe_number_by_ingredient("Bell pepper")


if __name__ == "__main__":
    main()