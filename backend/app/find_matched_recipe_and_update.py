import pandas as pd
import ast
import time
from app.generate_meal_plan import gen_shopping_list, insert_status_nutrient_info
from app.post_process_with_real_snack import process_recipe


def find_matched_recipe_and_update(response, recipe_id):
    """
    Called in ./backend/app/routes.py.
    Find the recipe in the response and update the recipe's status to 'matched'.
    :param response: JSON object containing the meal plan
    :param recipe_id: string of the recipe ID
    :return: updated JSON object containing the meal plan
    """
    clicked_recipe = {}
    date_counter = 0
    recipe_counter = 0

    # Load the recipes pool from the CSV file
    recipe_df = pd.read_csv("./meal_db/meal_database.csv")

    all_recipes_df = pd.read_csv("./meal_db/meal_database_V2.csv")

    snack_recipes_df = all_recipes_df[all_recipes_df["meal_slot"] == "['snack']"]

    # Traverse the response to find and remove the clicked recipe
    for day in response["days"]:
        for i, recipe in enumerate(day["recipes"]):
            if recipe["id"] == recipe_id:
                clicked_recipe = day["recipes"].pop(i)
                recipe_counter = i
                break
        if clicked_recipe:
            break
        date_counter += 1

    # Check if clicked_recipe has been found
    if not clicked_recipe:
        raise ValueError("No recipe found with the specified ID.")

    # Ensure 'id' is an integer
    clicked_recipe["id"] = int(clicked_recipe["id"])

    # Call find_matched_recipe with the clicked_recipe
    recipe_to_replace = find_matched_recipe(clicked_recipe, recipe_df, snack_recipes_df)

    # Ensure that a matched recipe is found before proceeding
    if recipe_to_replace:
        recipe_to_replace["meal_name"] = clicked_recipe["meal_name"]

        # Update the recipe at the same position
        response["days"][date_counter]["recipes"].insert(
            recipe_counter, recipe_to_replace
        )

        # Update nutrition values and other related data

        if clicked_recipe["meal_slot"] == "['lunch', 'dinner']":
            response = update_nutrition_values(
                response, clicked_recipe, "subtract", recipe_df, snack_recipes_df
            )
            response = update_nutrition_values(
                response, recipe_to_replace, "add", recipe_df, snack_recipes_df
            )
        time.sleep(0.1)
        response = gen_shopping_list(response)
        response = insert_status_nutrient_info(response)

        output_data = {"meal_plan": response, "id_to_replace": recipe_to_replace["id"]}
        return output_data
    else:
        raise ValueError("No matched recipe found")


def find_matched_recipe(recipe, recipe_df, snack_df):
    """
    Finds a recipe in the recipes_pool with calories number closest to the original one,
    and returns it in the format expected by the frontend.

    :param recipe: Dictionary with recipe details including the 'id' key
    :return: Dictionary with matched recipe details in the expected format
    """
    print("find_matched_recipe called with recipe:", recipe)

    # Ensure the recipe has an 'id' key
    if "id" not in recipe:
        print("Debug: Recipe dictionary keys are:", recipe.keys())
        raise KeyError("The recipe does not contain an 'id' key.")

    # Additional debug print to ensure id is being correctly accessed
    print(f"Recipe ID being used for lookup: {recipe['id']}")

    # Ensure 'id' is an integer
    recipe_id = int(recipe["id"])

    if recipe["meal_slot"] == "['lunch', 'dinner']":
        # Find the calories of the original recipe
        original_recipe_row = recipe_df.loc[recipe_df["number"] == recipe_id]
        print("Original Recipe Row:\n", original_recipe_row)

        if original_recipe_row.empty:
            print("No recipe found with the given id:", recipe["id"])
            return None  # Handle the case where the recipe is not found

        original_calories = original_recipe_row["energy_kcal"].values[0]
        print("Original calories:", original_calories)

        # Calculate the absolute difference between the original recipe's calories and each recipe's calories
        recipe_df["calories_diff"] = (
            recipe_df["energy_kcal"] - original_calories
        ).abs()

        # Filter out the rows where the number equals the original recipe's number
        filtered_recipe_df = recipe_df[recipe_df["number"] != recipe_id]

        # Find the row with the minimum calories difference from the remaining rows
        matched_recipe_row = filtered_recipe_df.loc[
            filtered_recipe_df["calories_diff"].idxmin()
        ]

        # Convert the matched recipe row to the expected dictionary format
        matched_recipe = {
            "carbohydrates": matched_recipe_row["carbohydrates_g"],
            "country": matched_recipe_row["country"],
            "fat": matched_recipe_row["fats_total_g"],
            "price": "N/A",
            "protein": matched_recipe_row["protein_g"],
            "region": matched_recipe_row["region"],
            "title": matched_recipe_row["title"],
            "ingredients": matched_recipe_row["ingredients"],
            "calories": matched_recipe_row["energy_kcal"],
            "meal_slot": matched_recipe_row["meal_slot"],
            "id": matched_recipe_row["number"],
            "cook_time": matched_recipe_row["cooktime"],
            "prep_time": matched_recipe_row["preptime"],
            "sub_region": matched_recipe_row["subregion"],
        }

        matched_recipe["ingredients"] = ast.literal_eval(matched_recipe["ingredients"])
    else:
        print("debug message")
        original_recipe_row = snack_df.loc[snack_df["number"] == recipe_id]
        print("Original Recipe Row:\n", original_recipe_row)

        if original_recipe_row.empty:
            print("No recipe found with the given id:", recipe["id"])
            return None  # Handle the case where the recipe is not found

        # Filter out the rows where the number equals the original recipe's number
        filtered_recipe_df = snack_df[snack_df["number"] != recipe_id]

        # Find the row with the minimum calories difference from the remaining rows
        matched_recipe_row = filtered_recipe_df.sample(n=1).iloc[0]

        matched_recipe = process_recipe(matched_recipe_row)

    for key, value in matched_recipe.items():
        matched_recipe[key] = f"{value}"

    print("New id found is", matched_recipe["id"])

    return matched_recipe


def update_nutrition_values(response, recipe, operation, recipe_df, snack_df):
    """
    Updates the nutrition values in response['tableData'] based on the matched recipe from the CSV file.
    :param response: JSON object containing the meal plan
    :param recipe: dict containing the recipe information
    :param operation: string of the operation to perform (add or subtract)
    :return: updated JSON object containing the meal plan
    """

    # Convert recipe ID to integer
    recipe["id"] = int(recipe["id"])

    if recipe["meal_slot"] == "['lunch', 'dinner']":
        # Find the original recipe row in the DataFrame
        original_recipe_row = recipe_df.loc[recipe_df["number"] == recipe["id"]]
    else:
        original_recipe_row = snack_df.loc[snack_df["number"] == recipe["id"]]

    if original_recipe_row.empty:
        raise ValueError(f"Recipe with ID {recipe['id']} not found in the database")

    # Define the nutrients to update based on the provided CSV columns
    nutrients = {
        "energy (calories)": "energy_kcal",
        "fiber (g)": "fibre_g",
        "carbohydrates (g)": "carbohydrates_g",
        "protein (g)": "protein_g",
        "fats (g)": "fats_total_g",
        "calcium (mg)": "calcium_mg",
        "sodium (mg)": "sodium_mg",
        "copper (mg)": "copper_mg",
        "fluoride (mg)": "fluoride_mg",
        "iron (mg)": "iron_mg",
        "magnesium (mg)": "magnesium_mg",
        "manganese (mg)": "manganese_mg",
        "potassium (mg)": "potassium_mg",
        "selenium (ug)": "selenium_ug",
        "zinc (mg)": "zinc_mg",
        "vitamin_a (iu)": "vitamin_A_iu",
        "thiamin (mg)": "thiamin_mg",
        "riboflavin (mg)": "riboflavin_mg",
        "niacin (mg)": "niacin_mg",
        "vitamin_b5 (mg)": "vitamin_B5_pantothenic_acid_mg",
        "vitamin_b6 (mg)": "vitamin_B6_mg",
        "vitamin_b12 (ug)": "vitamin_B12_ug",
        "folate (ug)": "folate_DFE_ug",
        "vitamin_c (mg)": "vitamin_C_total_ascorbic_acid_mg",
        "vitamin_d (iu)": "vitiamin_D_IU",
        "vitamin_e (mg)": "vitamin_E_alphatocopherol_mg",
        "choline (mg)": "choline_mg",
        "vitamin_k (ug)": "vitamin_K_phylloquinone_ug",
    }

    # Update the tableData values
    for item in response["tableData"]:
        nutrient_name = item["nutrientName"].lower()
        if nutrient_name in nutrients:
            csv_key = nutrients[nutrient_name]
            if csv_key in original_recipe_row.columns:
                value = float(original_recipe_row[csv_key].values[0])
                if operation == "add":
                    item["actual"] += value
                    item["actual"] = int(round(item["actual"]))
                elif operation == "subtract":
                    item["actual"] -= value
                    item["actual"] = int(round(item["actual"]))

    return response


def main():
    recipe = {
        "calories": "108.3",
        "carbohydrates": "9.8139",
        "cook_time": "20 minutes",
        "country": "US",
        "fat": "7.2",
        "id": "15912",
        "ingredients": ["potato", "butter", "salt", "brown sugar", "cinnamon"],
        "meal_name": "Breakfast",
        "meal_slot": "['lunch', 'dinner']",
        "prep_time": "15 minutes",
        "price": "N/A",
        "protein": "2.6787",
        "region": "North American ",
        "sub_region": "US ",
        "title": "Cinnamon Sweet Potato Chips",
        "type": "normal",
    }

    response = update_nutrition_values(recipe)
    print(f"Matched Recipe:\n{recipe}")


if __name__ == "__main__":
    main()
