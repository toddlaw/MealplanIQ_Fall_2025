import datetime
from app.check_privileges import check_registered
from app.calculate_bmi import bmi_calculator_function
from app.calculate_energy import energy_calculator_function
from app.calculate_nutritional_requirements import calculate_macros, calculate_micros
from app.apply_user_prefs_to_meal_database import apply_user_prefs
from app.retrieve_diet import get_diet_plan
from app.adjust_nutritional_requirements import adjust_nutrients
from app.find_optimal_meals import optimize_meals_integration
from app.V2_post_process import post_process_results
# from app.post_process_with_real_snack import process_the_recipes_with_snacks
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
    upper_bound = float("inf") if not parts[1].strip() else int(
        parts[1].strip())

    if actual != 0 and lower_bound == 0 and not parts[1].strip():
        return False
    return lower_bound <= actual <= upper_bound


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
    all_recipes_df = pd.read_csv("./meal_db/meal_database.csv")

    snack_recipes_df = all_recipes_df[all_recipes_df["meal_slot"]
                                      == "['snack']"]

    # 5. Apply user prefs to meal database
    recipes_with_scores = apply_user_prefs(
        data["favouriteCuisines"],
        data["dietaryConstraint"],
        data["religiousConstraint"],
        data["likedFoods"],
        data["dislikedFoods"],
        data["allergies"],
        all_recipes_df,
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


    # Calculating the difference in days
    difference = max_date - min_date
    days = difference.days + 1

    if "nutrient" in diet_info["nutrients"]:
        list_of_excluded_nutrients = list(
            diet_info["nutrients"]["nutrient"].values())
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
            str(nutrient).lower() for nutrient in list_of_excluded_nutrients
        ],
        constraint_relaxation=constraint_relaxation,
        exclude=data["excludedRecipes"],
        include=data["includedRecipes"],
    )

    # optimized_snacks = []
    # print('11-22-3', optimized_snacks)
    # print('11-22-4', optimized_results['recipes'])

    '''
    Note: for optimized_results, a meal_slot might have all breakfast, lunch and main. 
    Then main and lunch have the priority since both of them are restrict to one. 
    '''

    # 9. Post-process response
    response = post_process_results(
        recipes_with_scores, optimized_results, min_date, days
    )

    # response = process_type_normal(response)
    # print("response6:", response)
    response = insert_status_nutrient_info(response)
    # print("response7:", response)
    response = gen_shopping_list(response)
    print("\n\nresponse8:\n\n", response)

    return response
