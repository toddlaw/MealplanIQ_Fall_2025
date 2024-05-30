import pandas as pd


def find_best_snack_match(snack_recipe_df, cumulative_nutrition, nutrition_key):
    def calculate_difference(snack_row):
        return abs(cumulative_nutrition - snack_row[nutrition_key])

    selected_snacks = pd.DataFrame()
    remaining_nutrition = cumulative_nutrition

    while not snack_recipe_df.empty:
        snack_recipe_df["difference"] = snack_recipe_df.apply(
            calculate_difference, axis=1
        )
        best_match = snack_recipe_df.nsmallest(1, "difference")
        selected_snacks = pd.concat([selected_snacks, best_match])

        remaining_nutrition -= best_match.iloc[0][nutrition_key]
        snack_recipe_df = snack_recipe_df.drop(best_match.index)

        if abs(remaining_nutrition) < 100:
            break

    return selected_snacks, remaining_nutrition


def process_the_recipes_with_snacks(snack_recipes):
    recipe_df = pd.read_csv("./meal_db/meal_database.csv")
    snack_recipe_df = pd.read_csv("./meal_db/snacks.csv")

    nutrition_key = "energy_kcal"
    cumulative_nutrition = sum(float(recipe["calories"]) for recipe in snack_recipes)

    selected_snacks_df, remaining_nutrition = find_best_snack_match(
        snack_recipe_df, cumulative_nutrition, nutrition_key
    )

    best_snack_match = selected_snacks_df.apply(process_recipe, axis=1).tolist()

    final_differences = cumulative_nutrition - selected_snacks_df[nutrition_key].sum()

    return best_snack_match


def process_recipe(recipe_row):
    return {
        "carbohydrates": recipe_row["carbohydrates_g"],
        "country": "N/A",
        "fat": recipe_row["fats_total_g"],
        "price": "N/A",
        "protein": recipe_row["protein_g"],
        "region": "N/A",
        "title": recipe_row["title"],
        "ingredients": recipe_row["ingredients"],
        "calories": recipe_row["energy_kcal"],
        "meal_slot": recipe_row["meal_slot"],
        "id": recipe_row["number"],
        "cook_time": "N/A",
        "prep_time": "N/A",
        "sub_region": "N/A",
    }


def main():
    snack_recipes = [
        {
            "calories": "3.68",
            "carbohydrates": "1.1741",
            "cook_time": "10 minutes",
            "country": "Moroccan",
            "fat": "0.0387",
            "id": "2685",
            "ingredients": ["lemon", "water", "water", "lemon", "salt"],
            "meal_name": "Snack",
            "meal_slot": "['lunch', 'dinner']",
            "multiples": 1,
            "prep_time": "10 minutes",
            "price": "N/A",
            "protein": "0.115",
            "region": "African ",
            "sub_region": "Northern Africa ",
            "title": "Citrons Confits Express (Quick Preserved Lemons)",
            "type": "normal",
        },
        {
            "calories": "16.0",
            "carbohydrates": "3.736",
            "cook_time": "20 minutes",
            "country": "Mexican",
            "fat": "0.04",
            "id": "6833",
            "ingredients": ["chicken breast half", "onion", "green bell pepper"],
            "meal_name": "Snack",
            "meal_slot": "['lunch', 'dinner']",
            "multiples": 1,
            "prep_time": "10 minutes",
            "price": "N/A",
            "protein": "0.44",
            "region": "Latin American ",
            "sub_region": "Mexican ",
            "title": "Easy Chicken Taco Filling",
            "type": "normal",
        },
        {
            "calories": "84.7",
            "carbohydrates": "9.918",
            "cook_time": "65 minutes",
            "country": "Indian",
            "fat": "0.15",
            "id": "4053",
            "ingredients": ["chicken", "garlic", "garam masala", "lime"],
            "meal_name": "Snack",
            "meal_slot": "['lunch', 'dinner']",
            "multiples": 1,
            "prep_time": "5 minutes",
            "price": "N/A",
            "protein": "1.908",
            "region": "Asian ",
            "sub_region": "Indian Subcontinent ",
            "title": "Masala-Spiced Roast Chicken",
            "type": "normal",
        },
    ]

    best_snack_match = process_the_recipes_with_snacks(snack_recipes)


if __name__ == "__main__":
    main()
