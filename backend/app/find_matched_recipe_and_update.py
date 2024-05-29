import pandas as pd
import ast

from app.generate_meal_plan import gen_shopping_list, insert_status_nutrient_info


def find_matched_recipe_and_update(response, recipe_id):
    """
    Called in ./backend/app/routes.py.
    Find the recipe in the response and update the recipe's status to 'matched'.
    :param response: JSON object containing the meal plan
    :param recipe_id: string of the recipe ID
    :return: updated JSON object containing the meal plan
    """
    recipe_to_replce = {}
    clicked_recipe = {}
    date_counter = 0
    for day in response["days"]:
        date_counter += 1
        for i, recipe in enumerate(day["recipes"]):
            if recipe["id"] == recipe_id:
                # Replace the recipe in place
                clicked_recipe = day["recipes"][i]
                break
    recipe_to_replce = find_matched_recipe(clicked_recipe)
    response["days"][date_counter]["recipes"].append(recipe_to_replce)
    response = update_nutrition_values(response, recipe_id, "subtract")
    response = update_nutrition_values(response, recipe_to_replce["id"], "add")
    response = gen_shopping_list(response)
    response = insert_status_nutrient_info(response)


    return response



def find_matched_recipe(recipe):
    """
    Finds a recipe in the recipes_pool with calories number closest to the original one,
    and returns it in the format expected by the frontend.

    :param recipe: Dictionary with recipe details including the 'id' key
    :return: Dictionary with matched recipe details in the expected format
    """
    # Load the recipes pool from the CSV file
    recipe_df = pd.read_csv("./meal_db/meal_database.csv")
    # Find the calories of the original recipe
    original_recipe_row = recipe_df.loc[recipe_df["number"] == int(recipe["id"])]

    print("Original Recipe Row:\n", original_recipe_row)

    if original_recipe_row.empty:
        return None  # or handle the case where the recipe is not found

    original_calories = original_recipe_row["energy_kcal"].values[0]
    print(original_calories)

    # Find the recipe with calories closest to the original recipe's calories
    recipe_df["calories_diff"] = (recipe_df["energy_kcal"] - original_calories).abs()
    matched_recipe_row = recipe_df.loc[recipe_df["calories_diff"].idxmin()]

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

    for key, value in matched_recipe.items():
        matched_recipe[key] = f"{value}"

    # Convert ingredients from a string to a list
    matched_recipe["ingredients"] = ast.literal_eval(matched_recipe["ingredients"])

    return matched_recipe


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

    recipe = find_matched_recipe(recipe)
    print(f"Matched Recipe:\n{recipe}")


def update_nutrition_values(response, recipe_id, operation):
    """
    Updates the nutrition values in response['tableData'] based on the matched recipe from the CSV file.
    :param response: JSON object containing the meal plan
    :param recipe_id: string of the recipe ID
    :param operation: string of the operation to perform (add or subtract)
    :return: updated JSON object containing the meal plan
    """
    # Find the matched recipe
    clicked_recipe = {}
    for day in response["days"]:
        for recipe in day["recipes"]:
            if recipe["id"] == recipe_id:
                clicked_recipe = recipe
                break

    matched_recipe = find_matched_recipe(clicked_recipe)
    if not matched_recipe:
        return response  # handle case where no matched recipe is found

    # Define the nutrients to update
    nutrients = {
        "energy (calories)": "calories",
        "fiber (g)": "fibre_g",
        "carbohydrates (g)": "carbohydrates_g",
        "protein (g)": "protein_g",
        "fats (g)": "fat",
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
        "vitamin_d (iu)": "vitamin_D_IU",
        "vitamin_e (mg)": "vitamin_E_alphatocopherol_mg",
        "choline (mg)": "choline_mg",
        "vitamin_k (ug)": "vitamin_K_phylloquinone_ug",
    }

    # Update the tableData values
    for item in response['tableData']:
        nutrient_name = item['nutrientName']
        if nutrient_name in nutrients:
            csv_key = nutrients[nutrient_name]
            if csv_key in matched_recipe:
                if operation == "add":
                    item['actual'] += float(matched_recipe[csv_key])
                elif operation == "subtract":
                    item['actual'] -= float(matched_recipe[csv_key])

    return response


if __name__ == "__main__":
    main()
