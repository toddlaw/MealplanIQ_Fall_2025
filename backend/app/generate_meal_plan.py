from app.check_privileges import check_registered
from app.calculate_bmi import bmi_calculator_function
from app.calculate_energy import energy_calculator_function
from app.calculate_nutritional_requirements import calculate_macros, \
    calculate_micros
from app.apply_user_prefs_to_meal_database import apply_user_prefs
from app.retrieve_diet import get_diet_plan
from app.adjust_nutritional_requirements import adjust_nutrients
from app.find_optimal_meals import optimize_meals_integration
from app.post_process import post_process_results


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

    #convert heights and weights if necessary
    for person in data['people']:
        if data['selectedUnit'] == 'imperial':
            person['weight'] = person['weight'] * 0.453592
            person['height'] = person['height'] * 2.54
        bmi.append(bmi_calculator_function(person['weight'], person['height']))

    # 3. Calculate energy
    energy = []

    for i, person in enumerate(data['people']):
        energy.append(
            energy_calculator_function(person['age'], bmi[i], person['gender'],
                                       person['weight'], person['height'],
                                       person['activityLevel']))

    # 4. Calculate nutritional requirements
    macros = calculate_macros(energy, data['people'])

    micros = calculate_micros(data['people'])

    # 5. Apply user prefs to meal database
    recipes_with_scores = apply_user_prefs(data['favouriteCuisines'],
                                           data['dietaryConstraint'],
                                           data['religiousConstraint'],
                                           data['likedFoods'],
                                           data['dislikedFoods'],
                                           data['allergies'])

    # 6. Retrieve diet
    diet_info = get_diet_plan(data['healthGoal'])

    # 7. Adjust nutritional requirements
    adjust_nutrients(macros, micros, diet_info['plan'], data['people'])

    MILLISECONDS_IN_DAY = 86400 * 1000
    days = int((data["maxDate"] - data["minDate"]) / MILLISECONDS_IN_DAY)

    if "nutrient" in diet_info["nutrients"]:
        list_of_excluded_nutrients = list(
            diet_info["nutrients"]["nutrient"].values())
    else:
        list_of_excluded_nutrients = []

    constraint_relaxation = 0.5
    # 8. Optimization fit
    optimized_results = optimize_meals_integration(
        recipe_df=recipes_with_scores, macros=macros, micros=micros,
        user_diet=diet_info["diet_score"], days=days,
        excluded_nutrients=[nutrient.lower() for nutrient in list_of_excluded_nutrients],
        constraint_relaxation=constraint_relaxation, exclude=data["excludedRecipes"],
        include=data["includedRecipes"])

    # 9. Post-process response
    response = post_process_results(recipes_with_scores, optimized_results, days)

    return response
