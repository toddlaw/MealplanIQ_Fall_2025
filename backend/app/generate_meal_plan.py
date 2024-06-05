import datetime
from app.check_privileges import check_registered
from app.calculate_bmi import bmi_calculator_function
from app.calculate_energy import energy_calculator_function
from app.calculate_nutritional_requirements import calculate_macros, calculate_micros
from app.apply_user_prefs_to_meal_database import apply_user_prefs
from app.retrieve_diet import get_diet_plan
from app.adjust_nutritional_requirements import adjust_nutrients
from app.find_optimal_meals import optimize_meals_integration
from app.post_process import post_process_results
from app.post_process_with_real_snack import process_the_recipes_with_snacks
import json
import os
import pandas as pd


def process_type_normal(response):
    """
    This method is a test phase to give all recipes a hard coded type of "normal".

    It should be erased after the normal and simple recipe logic is completed.

    :param response: response object
    :return: response object with meal slot replaced with actual meal names
    """
    for day in response["days"]:
        for recipe in day["recipes"]:
            recipe["type"] = "normal"

    return response


def process_response_meal_name(response):
    """
    A part of this method is a test phase method to generate the meal name with actual meal names.

    :param response: response object
    :return: response object with meal slot replaced with actual meal names
    """

    # delete this part after the composite meal logic is completed
    for day in response["days"]:
        day["recipes"][0]["meal_name"] = "Breakfast"
        day["recipes"][1]["meal_name"] = "Lunch"
        day["recipes"][2]["meal_name"] = "Dinner"

    # Don't delete this!!!
    for snack in response["snacks"]:
        snack["meal_name"] = "Snack"

    return response


def gen_shopping_list(response):
    """
    This method returns the meal plan with the shopping list data generated based on each recipe ingredient names.
    Ensures the shopping list contains only unique elements.
    """
    shopping_list = set()
    for day in response["days"]:
        for recipe in day["recipes"]:
            if not isinstance(recipe["ingredients"], list):
                recipe["ingredients"] = ["N/A"]
                continue  # Skip this recipe if ingredients is not a list
            for ingredient in recipe["ingredients"]:
                if ingredient != "N/A":
                    shopping_list.add(ingredient)

    response["shopping_list"] = list(shopping_list)

    return response


def distribute_snacks_to_date(response):
    """
    Distribute snacks evenly across a given number of days, with an additional distribution of any remainder
    to minimize consecutive days without snacks.
    """
    days_len = len(response["days"])
    snacks_len = len(response["snacks"])

    min_num_snacks_in_a_day = snacks_len // days_len
    remainder = snacks_len % days_len

    snack_index = 0

    # Even distribution
    for day in response["days"]:
        for _ in range(min_num_snacks_in_a_day):
            day["recipes"].append(response["snacks"][snack_index])
            snack_index += 1

    # Distribute the remainder in a way that minimizes consecutive days without snacks
    if remainder > 0:
        interval = days_len // remainder
        for i in range(remainder):
            response["days"][i * interval]["recipes"].append(
                response["snacks"][snack_index]
            )
            snack_index += 1

    return response


def insert_snacks_between_meals(response):
    """
    Insert snacks into the right snack time, one between breakfast and lunch, and the other between lunch and dinner.

    Ensure the number of snack recipes in the two positions are as close as possible, with a difference of at most +1.
    """
    for day in response["days"]:
        breakfast_indices = [
            i
            for i, recipe in enumerate(day["recipes"])
            if recipe["meal_name"].lower() == "breakfast"
        ]
        lunch_indices = [
            i
            for i, recipe in enumerate(day["recipes"])
            if recipe["meal_name"].lower() == "lunch"
        ]
        dinner_indices = [
            i
            for i, recipe in enumerate(day["recipes"])
            if recipe["meal_name"].lower() == "dinner"
        ]

        snack_indices = [
            i
            for i, recipe in enumerate(day["recipes"])
            if recipe["meal_name"].lower() == "snack"
        ]
        snacks = [day["recipes"][i] for i in snack_indices]

        # Remove existing snacks from the list
        day["recipes"] = [
            recipe for i, recipe in enumerate(day["recipes"]) if i not in snack_indices
        ]

        # Determine insertion points
        insert_between_breakfast_lunch = (
            breakfast_indices[-1] + 1 if breakfast_indices else 0
        )
        insert_between_lunch_dinner = (
            lunch_indices[-1] + 1 if lunch_indices else len(day["recipes"])
        )

        # Split snacks into two approximately equal parts
        mid = (
            len(snacks) + 1
        ) // 2  # Ensure the first part has one more element if odd

        snacks1 = snacks[:mid]
        snacks2 = snacks[mid:]

        # Insert snacks into the right positions
        for snack in reversed(snacks1):
            day["recipes"].insert(insert_between_breakfast_lunch, snack)

        # Adjust the second insertion point after inserting the first batch of snacks
        insert_between_lunch_dinner += len(snacks1)

        for snack in reversed(snacks2):
            day["recipes"].insert(insert_between_lunch_dinner, snack)

    return response


def insert_status_nutrient_info(response):
    for nutrient in response["tableData"]:
        nutrient["display_target"] = nutrient["target"]
        if is_within_target(nutrient["actual"], nutrient["target"]):
            nutrient["status"] = "success"
        else:
            nutrient["status"] = "warning"

        if nutrient["display_target"].endswith("- "):
            nutrient["display_target"] = nutrient["display_target"][:-2]

    return response


def is_within_target(actual, target):
    parts = target.split("-")

    lower_bound = int(parts[0].strip())
    upper_bound = float("inf") if not parts[1].strip() else int(parts[1].strip())

    if actual != 0 and lower_bound == 0 and not parts[1].strip():
        return False
    return lower_bound <= actual <= upper_bound


def update_meals_with_snacks(response, snack_recipes_df):
    snacks = response["snacks"]
    new_snacks = process_the_recipes_with_snacks(snacks, snack_recipes_df)
    response["snacks"] = new_snacks
    print(response["snacks"])

    return response


def gen_meal_plan(data):
    """
    Called in ./backend/app/routes.py.
    Generates a meal plan with 9 steps based on the user data passed in from the frontend.
    :param data: dict of user data
    :return: dict of meal plan details
    """
    # 1. Check privileges
    # if not check_registered(data):
    #     return False

    # 2. Calculate BMI
    bmi = []

    # convert heights and weights if necessary
    for person in data["people"]:
        if data["selectedUnit"] == "imperial":
            person["weight"] = person["weight"] * 0.453592
            person["height"] = person["height"] * 2.54
        bmi.append(bmi_calculator_function(person["weight"], person["height"]))

    # 3. Calculate energy
    energy = []

    for i, person in enumerate(data["people"]):
        energy.append(
            energy_calculator_function(
                person["age"],
                bmi[i],
                person["gender"],
                person["weight"],
                person["height"],
                person["activityLevel"],
            )
        )

    # 4. Calculate nutritional requirements
    macros = calculate_macros(energy, data["people"])

    micros = calculate_micros(data["people"])

    all_recipes_df = pd.read_csv("./meal_db/meal_database_V2.csv")

    snack_recipes_df = all_recipes_df[all_recipes_df["meal_slot"] == "['snack']"]

    # 5. Apply user prefs to meal database
    recipes_with_scores = apply_user_prefs(
        data["favouriteCuisines"],
        data["dietaryConstraint"],
        data["religiousConstraint"],
        data["likedFoods"],
        data["dislikedFoods"],
        data["allergies"],
        pd.read_csv("./meal_db/meal_database.csv"),
    )

    # 6. Retrieve diet
    diet_info = get_diet_plan(data["healthGoal"])

    # 7. Adjust nutritional requirements
    adjust_nutrients(macros, micros, diet_info["plan"], data["people"])

    # Assuming data["minDate"] and data["maxDate"] are in milliseconds since the epoch
    min_date = datetime.datetime.fromtimestamp(
        data["minDate"] / 1000.0, datetime.timezone.utc
    )
    max_date = datetime.datetime.fromtimestamp(
        data["maxDate"] / 1000.0, datetime.timezone.utc
    )

    formatted_min_date = min_date.strftime("%Y/%m/%d")
    formatted_max_date = max_date.strftime("%Y/%m/%d")

    print("Min date:", formatted_min_date)
    print("Max date:", formatted_max_date)

    # Calculating the difference in days
    difference = max_date - min_date
    days = difference.days + 1

    print("Difference in days:", days)

    if "nutrient" in diet_info["nutrients"]:
        list_of_excluded_nutrients = list(diet_info["nutrients"]["nutrient"].values())
    else:
        list_of_excluded_nutrients = []

    constraint_relaxation = 0.5
    # 8. Optimization fit
    optimized_results = optimize_meals_integration(
        recipe_df=recipes_with_scores,
        macros=macros,
        micros=micros,
        user_diet=diet_info["diet_score"],
        days=days,
        excluded_nutrients=[
            nutrient.lower() for nutrient in list_of_excluded_nutrients
        ],
        constraint_relaxation=constraint_relaxation,
        exclude=data["excludedRecipes"],
        include=data["includedRecipes"],
    )

    # 9. Post-process response
    response = post_process_results(
        recipes_with_scores, optimized_results, min_date, days
    )

    response = update_meals_with_snacks(response, snack_recipes_df.copy())
    response = process_response_meal_name(response)
    response = distribute_snacks_to_date(response)
    response = insert_snacks_between_meals(response)
    response = process_type_normal(response)
    response = insert_status_nutrient_info(response)
    response = gen_shopping_list(response)

    return response


def main():
    # Construct the file path relative to the script location
    script_dir = os.path.dirname(__file__)
    message_file_path = os.path.join(script_dir, "message.json")
    output_file_path = os.path.join(script_dir, "output.json")

    # Load the JSON file as a dictionary
    with open(message_file_path, "r") as file:
        data = json.load(file)

    # Process the response
    response = process_response_meal_name(data)
    response = process_type_normal(response)
    response = distribute_snacks_to_date(response)
    response = insert_snacks_between_meals(response)

    # Write the response to a new JSON file
    with open(output_file_path, "w") as output_file:
        json.dump(response, output_file, indent=4)

    print("Response written to output.json")


if __name__ == "__main__":
    main()
