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
import json
import os


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
            if recipe["meal_name"] == "Breakfast"
        ]
        lunch_indices = [
            i
            for i, recipe in enumerate(day["recipes"])
            if recipe["meal_name"] == "Lunch"
        ]
        dinner_indices = [
            i
            for i, recipe in enumerate(day["recipes"])
            if recipe["meal_name"] == "Dinner"
        ]

        snack_indices = [
            i
            for i, recipe in enumerate(day["recipes"])
            if recipe["meal_name"] == "Snack"
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

    if parts[1].strip():
        lower_bound = int(parts[0].strip())
        upper_bound = int(parts[1].strip())
        return lower_bound <= actual <= upper_bound
    else:
        lower_bound = int(parts[0].strip())
        return actual >= lower_bound


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

    # 5. Apply user prefs to meal database
    recipes_with_scores = apply_user_prefs(
        data["favouriteCuisines"],
        data["dietaryConstraint"],
        data["religiousConstraint"],
        data["likedFoods"],
        data["dislikedFoods"],
        data["allergies"],
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

    response = process_response_meal_name(response)
    response = distribute_snacks_to_date(response)
    response = insert_snacks_between_meals(response)
    response = process_type_normal(response)
    response = insert_status_nutrient_info(response)

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
    # main()

    data = {
        "constraints_loosened": True,
        "days": [
            {
                "date": "2024-05-31",
                "date_weekday": "Friday May 31",
                "recipes": [
                    {
                        "calories": "229.971",
                        "carbohydrates": "56.2279",
                        "cook_time": "240 minutes",
                        "country": "US",
                        "fat": "0.0226",
                        "id": "16232",
                        "ingredients": [
                            "chicken breast half",
                            "white vinegar",
                            "brown sugar",
                            "garlic powder",
                            "red pepper flake",
                        ],
                        "meal_name": "Breakfast",
                        "meal_slot": "['lunch', 'dinner']",
                        "prep_time": "10 minutes",
                        "price": "N/A",
                        "protein": "0.5791",
                        "region": "North American ",
                        "sub_region": "US ",
                        "title": "Slow Cooker Barbeque Chicken",
                        "type": "normal",
                    },
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
                        "calories": "7.6115",
                        "carbohydrates": "1.4611",
                        "cook_time": "15 minutes",
                        "country": "Indian",
                        "fat": "0.2424",
                        "id": "4104",
                        "ingredients": [
                            "curry powder",
                            "red pepper flake",
                            "kosher salt",
                            "ginger",
                            "paprika",
                            "cinnamon",
                            "turmeric",
                            "water",
                            "chicken breast half",
                        ],
                        "meal_name": "Snack",
                        "meal_slot": "['lunch', 'dinner']",
                        "multiples": 1,
                        "prep_time": "15 minutes",
                        "price": "N/A",
                        "protein": "0.3059",
                        "region": "Asian ",
                        "sub_region": "Indian Subcontinent ",
                        "title": "Tandoori Chicken II",
                        "type": "normal",
                    },
                    {
                        "calories": "8.7558",
                        "carbohydrates": "1.6001",
                        "cook_time": "10 minutes",
                        "country": "US",
                        "fat": "0.3557",
                        "id": "14801",
                        "ingredients": [
                            "paprika",
                            "salt",
                            "cayenne pepper",
                            "cumin",
                            "thyme",
                            "white pepper",
                            "onion powder",
                            "chicken breast half",
                        ],
                        "meal_name": "Snack",
                        "meal_slot": "['lunch', 'dinner']",
                        "multiples": 1,
                        "prep_time": "10 minutes",
                        "price": "N/A",
                        "protein": "0.3836",
                        "region": "North American ",
                        "sub_region": "US ",
                        "title": "Blackened Chicken",
                        "type": "normal",
                    },
                    {
                        "calories": "345.3205",
                        "carbohydrates": "35.885",
                        "cook_time": "35 minutes",
                        "country": "French",
                        "fat": "18.1084",
                        "id": "9766",
                        "ingredients": [
                            "vegetable oil",
                            "chicken",
                            "salt",
                            "black pepper",
                            "garlic powder",
                            "red wine",
                            "chicken stock",
                            "onion",
                            "cornstarch",
                            "water",
                        ],
                        "meal_name": "Lunch",
                        "meal_slot": "['lunch', 'dinner']",
                        "prep_time": "10 minutes",
                        "price": "N/A",
                        "protein": "11.0408",
                        "region": "European ",
                        "sub_region": "French ",
                        "title": "Easy Coq Au Vin",
                        "type": "normal",
                    },
                    {
                        "calories": "16.0",
                        "carbohydrates": "3.736",
                        "cook_time": "20 minutes",
                        "country": "Mexican",
                        "fat": "0.04",
                        "id": "6833",
                        "ingredients": [
                            "chicken breast half",
                            "onion",
                            "green bell pepper",
                        ],
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
                        "calories": "44.7",
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
                    {
                        "calories": "360.867",
                        "carbohydrates": "32.9678",
                        "cook_time": "5 minutes",
                        "country": "US",
                        "fat": "21.8124",
                        "id": "17625",
                        "ingredients": ["butter", "garlic powder", "white vinegar"],
                        "meal_name": "Dinner",
                        "meal_slot": "['lunch', 'dinner']",
                        "prep_time": "5 minutes",
                        "price": "N/A",
                        "protein": "12.8305",
                        "region": "North American ",
                        "sub_region": "US ",
                        "title": "Rule of 3 - Garlic Buffalo Wing Sauce",
                        "type": "normal",
                    },
                ],
            },
            {
                "date": "2024-05-30",
                "date_weekday": "Thursday May 30",
                "recipes": [
                    {
                        "calories": "230.97",
                        "carbohydrates": "8.7474",
                        "cook_time": "8 minutes",
                        "country": "Egyptian",
                        "fat": "19.4841",
                        "id": "2630",
                        "ingredients": ["purpose flour", "salt", "milk", "olive oil"],
                        "meal_name": "Breakfast",
                        "meal_slot": "['lunch', 'dinner']",
                        "prep_time": "15 minutes",
                        "price": "N/A",
                        "protein": "5.7645",
                        "region": "African ",
                        "sub_region": "Middle Eastern ",
                        "title": "Saboob (Egyptian Flatbread)",
                        "type": "normal",
                    },
                    {
                        "calories": "49.554",
                        "carbohydrates": "7.8748",
                        "cook_time": "60 minutes",
                        "country": "Italian",
                        "fat": "0.162",
                        "id": "10884",
                        "ingredients": [
                            "water",
                            "white sugar",
                            "yeast",
                            "salt",
                            "purpose flour",
                        ],
                        "meal_name": "Snack",
                        "meal_slot": "['lunch', 'dinner']",
                        "multiples": 1,
                        "prep_time": "20 minutes",
                        "price": "N/A",
                        "protein": "4.2984",
                        "region": "European ",
                        "sub_region": "Italian ",
                        "title": "Mama D's Italian Bread",
                        "type": "normal",
                    },
                    {
                        "calories": "56.6602",
                        "carbohydrates": "13.145",
                        "cook_time": "12 minutes",
                        "country": "US",
                        "fat": "0.255",
                        "id": "18512",
                        "ingredients": [
                            "orange juice",
                            "lime",
                            "honey",
                            "red pepper flake",
                            "chicken breast half",
                            "cilantro",
                        ],
                        "meal_name": "Snack",
                        "meal_slot": "['lunch', 'dinner']",
                        "multiples": 1,
                        "prep_time": "5 minutes",
                        "price": "N/A",
                        "protein": "0.8999",
                        "region": "North American ",
                        "sub_region": "US ",
                        "title": "Tropical Grilled Chicken Breast",
                        "type": "normal",
                    },
                    {
                        "calories": "68.64",
                        "carbohydrates": "0.9636",
                        "cook_time": "180 minutes",
                        "country": "French",
                        "fat": "0.2244",
                        "id": "9732",
                        "ingredients": ["egg white", "confectioner sugar"],
                        "meal_name": "Snack",
                        "meal_slot": "['lunch', 'dinner']",
                        "multiples": 1,
                        "prep_time": "20 minutes",
                        "price": "N/A",
                        "protein": "14.388",
                        "region": "European ",
                        "sub_region": "French ",
                        "title": "Authentic French Meringues",
                        "type": "normal",
                    },
                    {
                        "calories": "289.9616",
                        "carbohydrates": "44.2191",
                        "cook_time": "10 minutes",
                        "country": "Australian",
                        "fat": "3.5716",
                        "id": "5418",
                        "ingredients": [
                            "zucchini",
                            "bread crumb",
                            "black pepper",
                            "parmesan cheese",
                            "egg white",
                        ],
                        "meal_name": "Lunch",
                        "meal_slot": "['lunch', 'dinner']",
                        "prep_time": "5 minutes",
                        "price": "N/A",
                        "protein": "19.0291",
                        "region": "Australasian ",
                        "sub_region": "Australian ",
                        "title": "Baked Zucchini Chips",
                        "type": "normal",
                    },
                    {
                        "calories": "82.062",
                        "carbohydrates": "16.2731",
                        "cook_time": "20 minutes",
                        "country": "Chinese",
                        "fat": "0.162",
                        "id": "3033",
                        "ingredients": [
                            "yeast",
                            "water",
                            "purpose flour",
                            "white sugar",
                            "baking soda",
                        ],
                        "meal_name": "Snack",
                        "meal_slot": "['lunch', 'dinner']",
                        "multiples": 1,
                        "prep_time": "35 minutes",
                        "price": "N/A",
                        "protein": "4.2984",
                        "region": "Asian ",
                        "sub_region": "Chinese and Mongolian ",
                        "title": "Simple and Tasty Chinese Steamed Buns",
                        "type": "normal",
                    },
                    {
                        "calories": "85.5",
                        "carbohydrates": "3.9285",
                        "cook_time": "30 minutes",
                        "country": "Irish",
                        "fat": "7.2",
                        "id": "12997",
                        "ingredients": ["potato", "salt", "purpose flour", "butter"],
                        "meal_name": "Snack",
                        "meal_slot": "['lunch', 'dinner']",
                        "multiples": 1,
                        "prep_time": "15 minutes",
                        "price": "N/A",
                        "protein": "2.6715",
                        "region": "European ",
                        "sub_region": "Irish ",
                        "title": "Irish Potato Farls",
                        "type": "normal",
                    },
                    {
                        "calories": "388.2604",
                        "carbohydrates": "100.4045",
                        "cook_time": "5 minutes",
                        "country": "Mexican",
                        "fat": "0.0035",
                        "id": "6463",
                        "ingredients": [
                            "water",
                            "white sugar",
                            "avocado",
                            "lime",
                            "salt",
                        ],
                        "meal_name": "Dinner",
                        "meal_slot": "['lunch', 'dinner']",
                        "prep_time": "20 minutes",
                        "price": "N/A",
                        "protein": "0.0212",
                        "region": "Latin American ",
                        "sub_region": "Mexican ",
                        "title": "Avocado Paletas",
                        "type": "normal",
                    },
                ],
            },
            {
                "date": "2024-05-29",
                "date_weekday": "Wednesday May 29",
                "recipes": [
                    {
                        "calories": "232.6",
                        "carbohydrates": "61.0093",
                        "cook_time": "30 minutes",
                        "country": "US",
                        "fat": "0.425",
                        "id": "14161",
                        "ingredients": ["apple", "cinnamon", "water", "brown sugar"],
                        "meal_name": "Breakfast",
                        "meal_slot": "['lunch', 'dinner']",
                        "prep_time": "15 minutes",
                        "price": "N/A",
                        "protein": "0.6824",
                        "region": "North American ",
                        "sub_region": "US ",
                        "title": "Delicious Apple Sauce",
                        "type": "normal",
                    },
                    {
                        "calories": "97.1408",
                        "carbohydrates": "2.7109",
                        "cook_time": "90 minutes",
                        "country": "US",
                        "fat": "9.3047",
                        "id": "13740",
                        "ingredients": [
                            "baking potato",
                            "olive oil",
                            "salt",
                            "butter",
                            "black pepper",
                            "cheddar cheese",
                        ],
                        "meal_name": "Snack",
                        "meal_slot": "['lunch', 'dinner']",
                        "multiples": 1,
                        "prep_time": "1 minutes",
                        "price": "N/A",
                        "protein": "1.7959",
                        "region": "North American ",
                        "sub_region": "US ",
                        "title": "Perfect Baked Potato",
                        "type": "normal",
                    },
                    {
                        "calories": "103.502",
                        "carbohydrates": "13.2078",
                        "cook_time": "3 minutes",
                        "country": "Italian",
                        "fat": "4.5118",
                        "id": "11039",
                        "ingredients": [
                            "purpose flour",
                            "white sugar",
                            "cinnamon",
                            "white wine",
                            "egg yolk",
                            "oil",
                        ],
                        "meal_name": "Snack",
                        "meal_slot": "['lunch', 'dinner']",
                        "multiples": 3,
                        "prep_time": "120 minutes",
                        "price": "N/A",
                        "protein": "2.6962",
                        "region": "European ",
                        "sub_region": "Italian ",
                        "title": "Cannoli Shells",
                        "type": "normal",
                    },
                    {
                        "calories": "108.3",
                        "carbohydrates": "9.8139",
                        "cook_time": "20 minutes",
                        "country": "US",
                        "fat": "7.2",
                        "id": "15912",
                        "ingredients": [
                            "potato",
                            "butter",
                            "salt",
                            "brown sugar",
                            "cinnamon",
                        ],
                        "meal_name": "Snack",
                        "meal_slot": "['lunch', 'dinner']",
                        "multiples": 3,
                        "prep_time": "15 minutes",
                        "price": "N/A",
                        "protein": "2.6787",
                        "region": "North American ",
                        "sub_region": "US ",
                        "title": "Cinnamon Sweet Potato Chips",
                        "type": "normal",
                    },
                    {
                        "calories": "285.2072",
                        "carbohydrates": "9.0246",
                        "cook_time": "60 minutes",
                        "country": "Indian",
                        "fat": "28.9289",
                        "id": "4070",
                        "ingredients": [
                            "chicken",
                            "lemon juice",
                            "salt",
                            "allspice",
                            "yogurt",
                            "lemon juice",
                            "vegetable oil",
                            "white vinegar",
                        ],
                        "meal_name": "Lunch",
                        "meal_slot": "['lunch', 'dinner']",
                        "prep_time": "20 minutes",
                        "price": "N/A",
                        "protein": "1.6322",
                        "region": "Asian ",
                        "sub_region": "Indian Subcontinent ",
                        "title": "Tandoori Chicken I",
                        "type": "normal",
                    },
                    {
                        "calories": "143.0",
                        "carbohydrates": "0.72",
                        "cook_time": "15 minutes",
                        "country": "German",
                        "fat": "9.51",
                        "id": "13246",
                        "ingredients": ["purpose flour", "egg"],
                        "meal_name": "Snack",
                        "meal_slot": "['lunch', 'dinner']",
                        "multiples": 1,
                        "prep_time": "10 minutes",
                        "price": "N/A",
                        "protein": "12.56",
                        "region": "European ",
                        "sub_region": "Deutschland ",
                        "title": "Spaetzle II",
                        "type": "normal",
                    },
                    {
                        "calories": "149.89",
                        "carbohydrates": "11.7097",
                        "cook_time": "15 minutes",
                        "country": "Irish",
                        "fat": "7.9788",
                        "id": "12967",
                        "ingredients": [
                            "milk",
                            "vinegar",
                            "purpose flour",
                            "salt",
                            "baking soda",
                        ],
                        "meal_name": "Snack",
                        "meal_slot": "['lunch', 'dinner']",
                        "multiples": 2,
                        "prep_time": "10 minutes",
                        "price": "N/A",
                        "protein": "7.686",
                        "region": "European ",
                        "sub_region": "Irish ",
                        "title": "Irish Soda Bread in a Skillet",
                        "type": "normal",
                    },
                    {
                        "calories": "408.0",
                        "carbohydrates": "86.364",
                        "cook_time": "45 minutes",
                        "country": "Canadian",
                        "fat": "3.0",
                        "id": "18778",
                        "ingredients": [
                            "purpose flour",
                            "wheat flour",
                            "salt",
                            "active yeast",
                            "water",
                        ],
                        "meal_name": "Dinner",
                        "meal_slot": "['lunch', 'dinner']",
                        "prep_time": "10 minutes",
                        "price": "N/A",
                        "protein": "15.852",
                        "region": "North American ",
                        "sub_region": "Canadian ",
                        "title": "Multigrain Bread",
                        "type": "normal",
                    },
                ],
            },
            {
                "date": "2024-05-28",
                "date_weekday": "Tuesday May 28",
                "recipes": [
                    {
                        "calories": "250.1088",
                        "carbohydrates": "9.7213",
                        "cook_time": "5 minutes",
                        "country": "French",
                        "fat": "14.4312",
                        "id": "9860",
                        "ingredients": [
                            "egg",
                            "white sugar",
                            "milk",
                            "cinnamon",
                            "salt",
                            "bread",
                        ],
                        "meal_name": "Breakfast",
                        "meal_slot": "['lunch', 'dinner']",
                        "prep_time": "5 minutes",
                        "price": "N/A",
                        "protein": "19.0001",
                        "region": "European ",
                        "sub_region": "French ",
                        "title": "Cinnamon-Accented French Toast",
                        "type": "normal",
                    },
                    {
                        "calories": "162.063",
                        "carbohydrates": "5.1805",
                        "cook_time": "5 minutes",
                        "country": "Japanese",
                        "fat": "9.5402",
                        "id": "5122",
                        "ingredients": ["egg", "water", "soy sauce", "white sugar"],
                        "meal_name": "Snack",
                        "meal_slot": "['lunch', 'dinner']",
                        "multiples": 2,
                        "prep_time": "5 minutes",
                        "price": "N/A",
                        "protein": "12.9914",
                        "region": "Asian ",
                        "sub_region": "Japanese ",
                        "title": "Japanese Sweet Omelet",
                        "type": "normal",
                    },
                    {
                        "calories": "168.005",
                        "carbohydrates": "8.5119",
                        "cook_time": "30 minutes",
                        "country": "Chinese",
                        "fat": "13.762",
                        "id": "3019",
                        "ingredients": [
                            "yeast",
                            "white sugar",
                            "purpose flour",
                            "water",
                            "water",
                            "purpose flour",
                            "salt",
                            "white sugar",
                            "vegetable oil",
                            "baking powder",
                        ],
                        "meal_name": "Snack",
                        "meal_slot": "['lunch', 'dinner']",
                        "multiples": 2,
                        "prep_time": "30 minutes",
                        "price": "N/A",
                        "protein": "4.2984",
                        "region": "Asian ",
                        "sub_region": "Chinese and Mongolian ",
                        "title": "Chinese Steamed Buns",
                        "type": "normal",
                    },
                    {
                        "calories": "173.9583",
                        "carbohydrates": "8.5014",
                        "cook_time": "10 minutes",
                        "country": "Mexican",
                        "fat": "14.4538",
                        "id": "6243",
                        "ingredients": [
                            "head cauliflower",
                            "water",
                            "lime",
                            "cilantro",
                            "butter",
                        ],
                        "meal_name": "Snack",
                        "meal_slot": "['lunch', 'dinner']",
                        "multiples": 1,
                        "prep_time": "15 minutes",
                        "price": "N/A",
                        "protein": "5.5312",
                        "region": "Latin American ",
                        "sub_region": "Mexican ",
                        "title": "Lime Cilantro Cauliflower Rice",
                        "type": "normal",
                    },
                    {
                        "calories": "264.811",
                        "carbohydrates": "11.5603",
                        "cook_time": "20 minutes",
                        "country": "Indian",
                        "fat": "20.1325",
                        "id": "4660",
                        "ingredients": [
                            "purpose flour",
                            "water",
                            "egg",
                            "butter",
                            "salt",
                            "caraway seed",
                        ],
                        "meal_name": "Lunch",
                        "meal_slot": "['lunch', 'dinner']",
                        "prep_time": "10 minutes",
                        "price": "N/A",
                        "protein": "12.9476",
                        "region": "Asian ",
                        "sub_region": "Indian Subcontinent ",
                        "title": "Indian Crepes",
                        "type": "normal",
                    },
                    {
                        "calories": "190.84",
                        "carbohydrates": "0.36",
                        "cook_time": "20 minutes",
                        "country": "Italian",
                        "fat": "18.255",
                        "id": "12345",
                        "ingredients": [
                            "russet potato",
                            "purpose flour",
                            "egg",
                            "olive oil",
                            "salt",
                        ],
                        "meal_name": "Snack",
                        "meal_slot": "['lunch', 'dinner']",
                        "multiples": 2,
                        "prep_time": "15 minutes",
                        "price": "N/A",
                        "protein": "6.28",
                        "region": "European ",
                        "sub_region": "Italian ",
                        "title": "Grandma's Gnocchi",
                        "type": "normal",
                    },
                    {
                        "calories": "202.966",
                        "carbohydrates": "24.2726",
                        "cook_time": "45 minutes",
                        "country": "Irish",
                        "fat": "7.9788",
                        "id": "13036",
                        "ingredients": [
                            "milk",
                            "white vinegar",
                            "purpose flour",
                            "white sugar",
                            "baking soda",
                            "salt",
                        ],
                        "meal_name": "Snack",
                        "meal_slot": "['lunch', 'dinner']",
                        "multiples": 1,
                        "prep_time": "10 minutes",
                        "price": "N/A",
                        "protein": "7.686",
                        "region": "European ",
                        "sub_region": "Irish ",
                        "title": "Brennan's Irish Soda Bread",
                        "type": "normal",
                    },
                    {
                        "calories": "522.4732",
                        "carbohydrates": "19.1989",
                        "cook_time": "20 minutes",
                        "country": "Indonesian",
                        "fat": "14.4408",
                        "id": "3454",
                        "ingredients": [
                            "vegetable oil",
                            "beef",
                            "onion",
                            "garlic",
                            "curry powder",
                            "head cabbage",
                            "ketchup",
                            "mango chutney",
                            "salt",
                            "water",
                        ],
                        "meal_name": "Dinner",
                        "meal_slot": "['lunch', 'dinner']",
                        "prep_time": "10 minutes",
                        "price": "N/A",
                        "protein": "81.017",
                        "region": "Asian ",
                        "sub_region": "Southeast Asian ",
                        "title": "Indonesian Curried Cabbage",
                        "type": "normal",
                    },
                ],
            },
        ],
        "snacks": [
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
                "calories": "7.6115",
                "carbohydrates": "1.4611",
                "cook_time": "15 minutes",
                "country": "Indian",
                "fat": "0.2424",
                "id": "4104",
                "ingredients": [
                    "curry powder",
                    "red pepper flake",
                    "kosher salt",
                    "ginger",
                    "paprika",
                    "cinnamon",
                    "turmeric",
                    "water",
                    "chicken breast half",
                ],
                "meal_name": "Snack",
                "meal_slot": "['lunch', 'dinner']",
                "multiples": 1,
                "prep_time": "15 minutes",
                "price": "N/A",
                "protein": "0.3059",
                "region": "Asian ",
                "sub_region": "Indian Subcontinent ",
                "title": "Tandoori Chicken II",
                "type": "normal",
            },
            {
                "calories": "8.7558",
                "carbohydrates": "1.6001",
                "cook_time": "10 minutes",
                "country": "US",
                "fat": "0.3557",
                "id": "14801",
                "ingredients": [
                    "paprika",
                    "salt",
                    "cayenne pepper",
                    "cumin",
                    "thyme",
                    "white pepper",
                    "onion powder",
                    "chicken breast half",
                ],
                "meal_name": "Snack",
                "meal_slot": "['lunch', 'dinner']",
                "multiples": 1,
                "prep_time": "10 minutes",
                "price": "N/A",
                "protein": "0.3836",
                "region": "North American ",
                "sub_region": "US ",
                "title": "Blackened Chicken",
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
                "calories": "44.7",
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
            {
                "calories": "49.554",
                "carbohydrates": "7.8748",
                "cook_time": "60 minutes",
                "country": "Italian",
                "fat": "0.162",
                "id": "10884",
                "ingredients": [
                    "water",
                    "white sugar",
                    "yeast",
                    "salt",
                    "purpose flour",
                ],
                "meal_name": "Snack",
                "meal_slot": "['lunch', 'dinner']",
                "multiples": 1,
                "prep_time": "20 minutes",
                "price": "N/A",
                "protein": "4.2984",
                "region": "European ",
                "sub_region": "Italian ",
                "title": "Mama D's Italian Bread",
                "type": "normal",
            },
            {
                "calories": "56.6602",
                "carbohydrates": "13.145",
                "cook_time": "12 minutes",
                "country": "US",
                "fat": "0.255",
                "id": "18512",
                "ingredients": [
                    "orange juice",
                    "lime",
                    "honey",
                    "red pepper flake",
                    "chicken breast half",
                    "cilantro",
                ],
                "meal_name": "Snack",
                "meal_slot": "['lunch', 'dinner']",
                "multiples": 1,
                "prep_time": "5 minutes",
                "price": "N/A",
                "protein": "0.8999",
                "region": "North American ",
                "sub_region": "US ",
                "title": "Tropical Grilled Chicken Breast",
                "type": "normal",
            },
            {
                "calories": "68.64",
                "carbohydrates": "0.9636",
                "cook_time": "180 minutes",
                "country": "French",
                "fat": "0.2244",
                "id": "9732",
                "ingredients": ["egg white", "confectioner sugar"],
                "meal_name": "Snack",
                "meal_slot": "['lunch', 'dinner']",
                "multiples": 1,
                "prep_time": "20 minutes",
                "price": "N/A",
                "protein": "14.388",
                "region": "European ",
                "sub_region": "French ",
                "title": "Authentic French Meringues",
                "type": "normal",
            },
            {
                "calories": "82.062",
                "carbohydrates": "16.2731",
                "cook_time": "20 minutes",
                "country": "Chinese",
                "fat": "0.162",
                "id": "3033",
                "ingredients": [
                    "yeast",
                    "water",
                    "purpose flour",
                    "white sugar",
                    "baking soda",
                ],
                "meal_name": "Snack",
                "meal_slot": "['lunch', 'dinner']",
                "multiples": 1,
                "prep_time": "35 minutes",
                "price": "N/A",
                "protein": "4.2984",
                "region": "Asian ",
                "sub_region": "Chinese and Mongolian ",
                "title": "Simple and Tasty Chinese Steamed Buns",
                "type": "normal",
            },
            {
                "calories": "85.5",
                "carbohydrates": "3.9285",
                "cook_time": "30 minutes",
                "country": "Irish",
                "fat": "7.2",
                "id": "12997",
                "ingredients": ["potato", "salt", "purpose flour", "butter"],
                "meal_name": "Snack",
                "meal_slot": "['lunch', 'dinner']",
                "multiples": 1,
                "prep_time": "15 minutes",
                "price": "N/A",
                "protein": "2.6715",
                "region": "European ",
                "sub_region": "Irish ",
                "title": "Irish Potato Farls",
                "type": "normal",
            },
            {
                "calories": "97.1408",
                "carbohydrates": "2.7109",
                "cook_time": "90 minutes",
                "country": "US",
                "fat": "9.3047",
                "id": "13740",
                "ingredients": [
                    "baking potato",
                    "olive oil",
                    "salt",
                    "butter",
                    "black pepper",
                    "cheddar cheese",
                ],
                "meal_name": "Snack",
                "meal_slot": "['lunch', 'dinner']",
                "multiples": 1,
                "prep_time": "1 minutes",
                "price": "N/A",
                "protein": "1.7959",
                "region": "North American ",
                "sub_region": "US ",
                "title": "Perfect Baked Potato",
                "type": "normal",
            },
            {
                "calories": "103.502",
                "carbohydrates": "13.2078",
                "cook_time": "3 minutes",
                "country": "Italian",
                "fat": "4.5118",
                "id": "11039",
                "ingredients": [
                    "purpose flour",
                    "white sugar",
                    "cinnamon",
                    "white wine",
                    "egg yolk",
                    "oil",
                ],
                "meal_name": "Snack",
                "meal_slot": "['lunch', 'dinner']",
                "multiples": 3,
                "prep_time": "120 minutes",
                "price": "N/A",
                "protein": "2.6962",
                "region": "European ",
                "sub_region": "Italian ",
                "title": "Cannoli Shells",
                "type": "normal",
            },
            {
                "calories": "108.3",
                "carbohydrates": "9.8139",
                "cook_time": "20 minutes",
                "country": "US",
                "fat": "7.2",
                "id": "15912",
                "ingredients": ["potato", "butter", "salt", "brown sugar", "cinnamon"],
                "meal_name": "Snack",
                "meal_slot": "['lunch', 'dinner']",
                "multiples": 3,
                "prep_time": "15 minutes",
                "price": "N/A",
                "protein": "2.6787",
                "region": "North American ",
                "sub_region": "US ",
                "title": "Cinnamon Sweet Potato Chips",
                "type": "normal",
            },
            {
                "calories": "143.0",
                "carbohydrates": "0.72",
                "cook_time": "15 minutes",
                "country": "German",
                "fat": "9.51",
                "id": "13246",
                "ingredients": ["purpose flour", "egg"],
                "meal_name": "Snack",
                "meal_slot": "['lunch', 'dinner']",
                "multiples": 1,
                "prep_time": "10 minutes",
                "price": "N/A",
                "protein": "12.56",
                "region": "European ",
                "sub_region": "Deutschland ",
                "title": "Spaetzle II",
                "type": "normal",
            },
            {
                "calories": "149.89",
                "carbohydrates": "11.7097",
                "cook_time": "15 minutes",
                "country": "Irish",
                "fat": "7.9788",
                "id": "12967",
                "ingredients": [
                    "milk",
                    "vinegar",
                    "purpose flour",
                    "salt",
                    "baking soda",
                ],
                "meal_name": "Snack",
                "meal_slot": "['lunch', 'dinner']",
                "multiples": 2,
                "prep_time": "10 minutes",
                "price": "N/A",
                "protein": "7.686",
                "region": "European ",
                "sub_region": "Irish ",
                "title": "Irish Soda Bread in a Skillet",
                "type": "normal",
            },
            {
                "calories": "162.063",
                "carbohydrates": "5.1805",
                "cook_time": "5 minutes",
                "country": "Japanese",
                "fat": "9.5402",
                "id": "5122",
                "ingredients": ["egg", "water", "soy sauce", "white sugar"],
                "meal_name": "Snack",
                "meal_slot": "['lunch', 'dinner']",
                "multiples": 2,
                "prep_time": "5 minutes",
                "price": "N/A",
                "protein": "12.9914",
                "region": "Asian ",
                "sub_region": "Japanese ",
                "title": "Japanese Sweet Omelet",
                "type": "normal",
            },
            {
                "calories": "168.005",
                "carbohydrates": "8.5119",
                "cook_time": "30 minutes",
                "country": "Chinese",
                "fat": "13.762",
                "id": "3019",
                "ingredients": [
                    "yeast",
                    "white sugar",
                    "purpose flour",
                    "water",
                    "water",
                    "purpose flour",
                    "salt",
                    "white sugar",
                    "vegetable oil",
                    "baking powder",
                ],
                "meal_name": "Snack",
                "meal_slot": "['lunch', 'dinner']",
                "multiples": 2,
                "prep_time": "30 minutes",
                "price": "N/A",
                "protein": "4.2984",
                "region": "Asian ",
                "sub_region": "Chinese and Mongolian ",
                "title": "Chinese Steamed Buns",
                "type": "normal",
            },
            {
                "calories": "173.9583",
                "carbohydrates": "8.5014",
                "cook_time": "10 minutes",
                "country": "Mexican",
                "fat": "14.4538",
                "id": "6243",
                "ingredients": [
                    "head cauliflower",
                    "water",
                    "lime",
                    "cilantro",
                    "butter",
                ],
                "meal_name": "Snack",
                "meal_slot": "['lunch', 'dinner']",
                "multiples": 1,
                "prep_time": "15 minutes",
                "price": "N/A",
                "protein": "5.5312",
                "region": "Latin American ",
                "sub_region": "Mexican ",
                "title": "Lime Cilantro Cauliflower Rice",
                "type": "normal",
            },
            {
                "calories": "190.84",
                "carbohydrates": "0.36",
                "cook_time": "20 minutes",
                "country": "Italian",
                "fat": "18.255",
                "id": "12345",
                "ingredients": [
                    "russet potato",
                    "purpose flour",
                    "egg",
                    "olive oil",
                    "salt",
                ],
                "meal_name": "Snack",
                "meal_slot": "['lunch', 'dinner']",
                "multiples": 2,
                "prep_time": "15 minutes",
                "price": "N/A",
                "protein": "6.28",
                "region": "European ",
                "sub_region": "Italian ",
                "title": "Grandma's Gnocchi",
                "type": "normal",
            },
            {
                "calories": "202.966",
                "carbohydrates": "24.2726",
                "cook_time": "45 minutes",
                "country": "Irish",
                "fat": "7.9788",
                "id": "13036",
                "ingredients": [
                    "milk",
                    "white vinegar",
                    "purpose flour",
                    "white sugar",
                    "baking soda",
                    "salt",
                ],
                "meal_name": "Snack",
                "meal_slot": "['lunch', 'dinner']",
                "multiples": 1,
                "prep_time": "10 minutes",
                "price": "N/A",
                "protein": "7.686",
                "region": "European ",
                "sub_region": "Irish ",
                "title": "Brennan's Irish Soda Bread",
                "type": "normal",
            },
        ],
        "tableData": [
            {
                "actual": 6825,
                "nutrientName": "energy (calories)",
                "target": "6200 - 6853",
            },
            {"actual": 61, "nutrientName": "fiber (g)", "target": "119 - "},
            {
                "actual": 692,
                "nutrientName": "carbohydrates (g)",
                "target": "959 - 1385",
            },
            {"actual": 316, "nutrientName": "protein (g)", "target": "213 - 746"},
            {"actual": 328, "nutrientName": "fats (g)", "target": "189 - 331"},
            {"actual": 3503, "nutrientName": "calcium (mg)", "target": "4000 - 10000"},
            {"actual": 9124, "nutrientName": "sodium (mg)", "target": "6000 - 9200"},
            {"actual": 5, "nutrientName": "copper (mg)", "target": "3 - 40"},
            {"actual": 22, "nutrientName": "fluoride (mg)", "target": "12 - 40"},
            {"actual": 44, "nutrientName": "iron (mg)", "target": "72 - 180"},
            {"actual": 1002, "nutrientName": "magnesium (mg)", "target": "1280 - "},
            {"actual": 11, "nutrientName": "manganese (mg)", "target": "6 - 44"},
            {"actual": 9152, "nutrientName": "potassium (mg)", "target": "18800 - "},
            {"actual": 500, "nutrientName": "selenium (ug)", "target": "220 - 1600"},
            {"actual": 44, "nutrientName": "zinc (mg)", "target": "32 - 160"},
            {"actual": 7965, "nutrientName": "vitamin_a (iu)", "target": "840 - 3600"},
            {"actual": 21, "nutrientName": "thiamin (mg)", "target": "4 - "},
            {"actual": 20, "nutrientName": "riboflavin (mg)", "target": "4 - "},
            {"actual": 144, "nutrientName": "niacin (mg)", "target": "56 - 140"},
            {"actual": 24, "nutrientName": "vitamin_b5 (mg)", "target": "20 - "},
            {"actual": 6, "nutrientName": "vitamin_b6 (mg)", "target": "5 - 400"},
            {"actual": 15, "nutrientName": "vitamin_b12 (ug)", "target": "9 - "},
            {"actual": 3648, "nutrientName": "folate (ug)", "target": "1600 - 4000"},
            {"actual": 152, "nutrientName": "vitamin_c (mg)", "target": "300 - 8000"},
            {"actual": 622, "nutrientName": "vitamin_d (iu)", "target": "2400 - 8000"},
            {"actual": 22, "nutrientName": "vitamin_e (mg)", "target": "60 - 4000"},
            {"actual": 2751, "nutrientName": "choline (mg)", "target": "1700 - 14000"},
            {"actual": 104, "nutrientName": "vitamin_k (ug)", "target": "360 - "},
        ],
    }
    insert_status_nutrient_info(data)
    print(data)
