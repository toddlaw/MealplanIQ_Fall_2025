"""
This file contains methods used to generate or help generate an optimal meal
plan for a given set of constraints. These constraints are to be passed into the
methods used for the generation of the meal plans.
"""
from pulp import *
import pandas as pd

def get_recipe_dict_from_df(recipe_df):
    """
    Takes in pandas dataframe for the meals_db.csv file and converts it into a
    dictionary of dictionaries. The purpose of this is to provide easy access
    to recipe information in optimize_meals_integration

    :param recipe_df: pandas dataframe of recipes
    :return: dictionary of dictionaries of recipe information i.e
    {
     "Calories: {
                  "Recipe_name_1": Calories_for_recipe_1,
                  "Recipe_name_2": Calories_for_recipe_2,
                  ....
                  "Recipe_name_n": Calories_for_recipe_n
                }
     "cholesterol": {
                     "Recipe_name_1": cholesterol_for_recipe_1,
                     "Recipe_name_2": cholesterol_for_recipe_2,
                      ....
                     "Recipe_name_n": cholesterol_for_recipe_n
                    }
    }
    """
    df = recipe_df
    df = df.drop(
        columns=['ingredients_with_quantities', 'cooking instructions'])
    df = df.dropna()
    nutrient_dict = {}
    recipes = list(df["number"])
    nutrient_dict["user_score"] = dict(zip(recipes, df["score"]))
    nutrient_dict["number"] = dict(zip(recipes, df["number"]))
    nutrient_dict["meal_type"] = dict(zip(recipes, df["meal_type"]))
    nutrient_dict["meal_slot"] = dict(zip(recipes, df["meal_slot"]))
    nutrient_dict["title"] = list(df["title"])
    nutrient_dict["Calories"] = dict(zip(recipes, df["energy_kcal"]))
    nutrient_dict["kj"] = dict(zip(recipes, df["energy_kj"]))
    nutrient_dict["fibre"] = dict(zip(recipes, df["fibre_g"]))
    nutrient_dict["carbohydrates"] = dict(zip(recipes, df["carbohydrates_g"]))
    nutrient_dict["starch"] = dict(zip(recipes, df["starch_g"]))
    nutrient_dict["cholesterol"] = dict(zip(recipes, df["cholesterol_mg"]))
    nutrient_dict["protein"] = dict(zip(recipes, df["protein_g"]))
    nutrient_dict["fats_total"] = dict(zip(recipes, df["fats_total_g"]))
    nutrient_dict["trans_fats"] = dict(
        zip(recipes, df["fatty_acids_total_trans_g"]))
    nutrient_dict["vitamin_A"] = nutrient_dict["number"] = dict(
        zip(recipes, df["vitamin_A_iu"]))
    nutrient_dict["thiamin"] = dict(zip(recipes, df["thiamin_mg"]))
    nutrient_dict["riboflavin"] = dict(zip(recipes, df["riboflavin_mg"]))
    nutrient_dict["niacin"] = dict(zip(recipes, df["niacin_mg"]))
    nutrient_dict["vitamin_B5"] = dict(
        zip(recipes, df["vitamin_B5_pantothenic_acid_mg"]))
    nutrient_dict["vitamin_B6"] = dict(zip(recipes, df["vitamin_B6_mg"]))
    nutrient_dict["vitamin_B12_added"] = dict(
        zip(recipes, df["vitamin B12_added_ug"]))
    nutrient_dict["vitamin_B12"] = dict(zip(recipes, df["vitamin_B12_ug"]))
    nutrient_dict["folate_total"] = dict(zip(recipes, df["folate_total_ug"]))
    nutrient_dict["folic_acid"] = dict(zip(recipes, df["folic_acid_g"]))
    nutrient_dict["vitamin_C"] = dict(
        zip(recipes, df["vitamin_C_total_ascorbic_acid_mg"]))
    nutrient_dict["vitamin_D"] = dict(zip(recipes, df["vitiamin_D_IU"]))
    nutrient_dict["vitamin_E"] = dict(
        zip(recipes, df["vitamin_E_alphatocopherol_mg"]))
    nutrient_dict["vitamin_E_added"] = dict(
        zip(recipes, df["vitamin_E_added_mg"]))
    nutrient_dict["vitamin_K"] = dict(
        zip(recipes, df["vitamin_K_phylloquinone_ug"]))
    nutrient_dict["choline"] = dict(zip(recipes, df["choline_mg"]))
    nutrient_dict["carotene_a"] = dict(zip(recipes, df["carotene_alpha_g"]))
    nutrient_dict["carotene_b"] = dict(zip(recipes, df["carotene_beta_g"]))
    nutrient_dict["calcium"] = dict(zip(recipes, df["calcium_mg"]))
    nutrient_dict["phosphorus"] = dict(zip(recipes, df["phosphorus_mg"]))
    nutrient_dict["potassium"] = dict(zip(recipes, df["potassium_mg"]))
    nutrient_dict["magnesium"] = dict(zip(recipes, df["magnesium_mg"]))
    nutrient_dict["sodium"] = dict(zip(recipes, df["sodium_mg"]))
    nutrient_dict["iron"] = dict(zip(recipes, df["iron_mg"]))
    nutrient_dict["copper"] = dict(zip(recipes, df["copper_mg"]))
    nutrient_dict["zinc"] = dict(zip(recipes, df["zinc_mg"]))
    nutrient_dict["manganese"] = dict(zip(recipes, df["manganese_mg"]))
    nutrient_dict["selenium"] = dict(zip(recipes, df["selenium_ug"]))
    nutrient_dict["flouride"] = dict(zip(recipes, df["fluoride_mg"]))

    return nutrient_dict


def optimize_meals_integration(recipe_df, macros, micros, user_diet,
                               days=1,exclude = [], include = [], excluded_nutrients = [],
                               constraint_relaxation=0.1):
    """
    This method generates a meal plan for a given set of constraints. If the
    first attempt at generating a meal plan fails, the constraints are relaxed
    until an optimal solution is found.

    :param recipe_df: pandas dataframe of recipes
    :param macros: dict of macronutrients
    :param micros: dict of micronutrients
    :param user_diet: dict of user diet
    :param days: int, number of days to generate meal plan for
    :param exclude: list of strings, names of recipes to exclude
    :param include: list of strings, names of recipes to include
    :param excluded_nutrients: list of strings, names of nutrients that we do
    not alter their constraint ranges if orginal solution is found to be infeasible
    :param constraint_relaxation: float, value between 0 and 1, how much to relax
    the constraint bounds by

    :return: dict of meal plan details form as shown below

    {
        "constraints_loosned": boolean,
        "recipes": [
                    {
                        "name": "recipe_name_1",
                        "multiples": 1
                    },
                    .. more recipes
                    ],
        "status": LPStatus, (most likeley Optimal or Infeasible),
        "constraint_targets": [
                                {
                                    "actual": calories fulfilled by meal plan,
                                    "name": "calories",
                                    "target": target calories (string range)
                                }
                                .. more constraint targets
                                ],
    }
    """

    # These constants are for finding ranges for hard set values such as Calories.
    # eating 2088 calories exact is hard so we take +- 5%
    LOWER_RANGE = 0.95
    UPPER_RANGE = 1.05

    # Indexes for minimum/maximum values for macros
    MIN_INDEX = 0
    MAX_INDEX = 1

    # Process Recipes dataframe
    recipe_dict = get_recipe_dict_from_df(recipe_df)

    # Update micros and macros to number of days
    micros = modifyUserConstraintsByDays(days, micros)
    macros = modifyUserConstraintsByDays(days, macros)

    # Create user ref and diet
    recipes = recipe_dict["number"]
    prob = LpProblem("Meal plan generation", LpMaximize)
    recipe_var = LpVariable.dicts("Recipes", recipes, lowBound=0,
                                  cat='Integer')

    """
    Macros
    """
    prob += lpSum(
        [recipe_var[i] * recipe_dict["user_score"][i] * user_diet[i] for i in
         recipes])


    prob += (
        lpSum(
            [recipe_dict["Calories"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= macros["large_calories"] * UPPER_RANGE,
        "Maxenergy_(calories)Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["Calories"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= (macros["large_calories"] * LOWER_RANGE),
        "Minenergy_(calories)Requirement",
    )

    prob += (
        lpSum([recipe_dict["fibre"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= macros["fiber_g"][MAX_INDEX],
        "Maxfiber_(g)Requirement",
    )

    prob += (
        lpSum([recipe_dict["fibre"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= macros["fiber_g"][MIN_INDEX],
        "Minfiber_(g)Requirement",
    )

    prob += (
        lpSum([recipe_dict["carbohydrates"][recipe] * recipe_var[recipe] for
               recipe in recipes]) <= macros["carbohydrates_g"][MAX_INDEX],
        "Maxcarbohydrates_(g)Requirement",
    )

    prob += (
        lpSum([recipe_dict["carbohydrates"][recipe] * recipe_var[recipe] for
               recipe in recipes]) >= macros["carbohydrates_g"][MIN_INDEX],
        "Mincarbohydrates_(g)Requirement",
    )

    prob += (
        lpSum([recipe_dict["protein"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= macros["protein_g"][MAX_INDEX],
        "Maxprotein_(g)Requirement",
    )

    prob += (
        lpSum([recipe_dict["protein"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= macros["protein_g"][MIN_INDEX],
        "Minprotein_(g)Requirement",
    )

    prob += (
        lpSum([recipe_dict["fats_total"][recipe] * recipe_var[recipe] for recipe
               in recipes]) <= macros["fat_g"][MAX_INDEX],
        "Maxfats_(g)Requirement",
    )

    prob += (
        lpSum([recipe_dict["fats_total"][recipe] * recipe_var[recipe] for recipe
               in recipes]) >= macros["fat_g"][MIN_INDEX],
        "Minfats_(g)Requirement",
    )


    """
    Micros
    """

    prob += (
        lpSum([recipe_dict["calcium"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= micros["min_calcium_mg_ul"],
        "Maxcalcium_(mg)Requirement",
    )

    prob += (
        lpSum([recipe_dict["calcium"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= micros["min_calcium_mg_ai"],
        "Mincalcium_(mg)Requirement",
    )
    #
    prob += (
        lpSum([recipe_dict["sodium"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= (micros["min_sodium_mg_ul"]),
        "Maxsodium_(mg)Requirement",
    )

    prob += (
        lpSum([recipe_dict["sodium"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= (micros["min_sodium_mg_ai"]),
        "Minsodium_(mg)Requirement",
    )
    #
    prob += (
        lpSum([recipe_dict["copper"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= micros["min_copper_mg_rda"],
        "Mincopper_(mg)Requirement",
    )

    prob += (
        lpSum([recipe_dict["copper"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= micros["min_copper_mg_ul"],
        "Maxcopper_(mg)Requirement",
    )
    #
    prob += (
        lpSum(
            [recipe_dict["flouride"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= micros["min_fluoride_mg_ai"],
        "Minfluoride_(mg)Requirement",
    )
    #
    prob += (
        lpSum(
            [recipe_dict["flouride"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= micros["min_fluoride_mg_ul"],
        "Maxfluoride_(mg)Requirement",
    )

    prob += (
        lpSum([recipe_dict["iron"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= micros["min_iron_mg_rda"],
        "Miniron_(mg)Requirement",
    )

    prob += (
        lpSum([recipe_dict["iron"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= micros["min_iron_mg_ul"],
        "Maxiron_(mg)Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["magnesium"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= micros["min_magnesium_mg_ul"],
        "Maxmagnesium_(mg)Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["magnesium"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= micros["min_magnesium_mg_rda"],
        "Minmagnesium_(mg)Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["manganese"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= micros["min_manganese_mg_ul"],
        "Maxmanganese_(mg)Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["manganese"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= micros["min_manganese_mg_rda"],
        "Minmanganese_(mg)Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["potassium"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= micros["min_potassium_mg_ai"],
        "Minpotassium_(mg)Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["potassium"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= micros["min_potassium_ul"],
        "Maxpotassium_(mg)Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["selenium"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= micros["min_selenium_ug_ul"],
        "Maxselenium_(ug)Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["selenium"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= micros["min_selenium_ug_rda"],
        "Minselenium_(ug)Requirement",
    )

    prob += (
        lpSum([recipe_dict["zinc"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= micros["min_zinc_mg_rda"],
        "Minzinc_(mg)Requirement",
    )

    prob += (
        lpSum([recipe_dict["zinc"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= micros["min_zinc_mg_ul"],
        "Maxzinc_(mg)Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["vitamin_A"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= micros["vit_a_iu_ul"],
        "Maxvitamin_a_(iu)Requirement",
    )
    prob += (
        lpSum(
            [recipe_dict["vitamin_A"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= micros["vit_a_iu_rda"],
        "Minvitamin_a_(iu)Requirement",
    )

    prob += (
        lpSum([recipe_dict["thiamin"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= micros["vit_b1_thiamin_mg_ul"],
        "Maxthiamin_(mg)Requirement",
    )

    prob += (
        lpSum([recipe_dict["thiamin"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= micros["vit_b1_thiamin_mg_rda"],
        "Minthiamin_(mg)Requirement",
    )

    prob += (
        lpSum([recipe_dict["riboflavin"][recipe] * recipe_var[recipe] for recipe
               in recipes]) <= micros["vit_b2_riboflavin_mg_ul"],
        "Maxriboflavin_(mg)Requirement",
    )

    prob += (
        lpSum([recipe_dict["riboflavin"][recipe] * recipe_var[recipe] for recipe
               in recipes]) >= micros["vit_b2_riboflavin_mg_rda"],
        "Minriboflavin_(mg)Requirement",
    )

    prob += (
        lpSum([recipe_dict["niacin"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= micros["vit_b3_niacin_mg_ul"],
        "Maxniacin_(mg)Requirement",
    )

    prob += (
        lpSum([recipe_dict["niacin"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= micros["vit_b3_niacin_mg_rda"],
        "Minniacin_(mg)Requirement",
    )

    prob += (
        lpSum([recipe_dict["vitamin_B5"][recipe] * recipe_var[recipe] for recipe
               in recipes]) <= micros["vit_b5_pantothenic_acid_mg_ul"],
        "Maxvitamin_b5_(mg)Requirement",
    )

    prob += (
        lpSum([recipe_dict["vitamin_B5"][recipe] * recipe_var[recipe] for recipe
               in recipes]) >= micros["vit_b5_pantothenicacid_mg_ai"],
        "Minvitamin_b5_(mg)Requirement",
    )

    prob += (
        lpSum([recipe_dict["vitamin_B6"][recipe] * recipe_var[recipe] for recipe
               in recipes]) <= micros["vit_b6_mg_ul"],
        "Maxvitamin_b6_(mg)Requirement",
    )

    prob += (
        lpSum([recipe_dict["vitamin_B6"][recipe] * recipe_var[recipe] for recipe
               in recipes]) >= micros["vit_b6_mg_rda"],
        "Minvitamin_b6_(mg)Requirement",
    )

    prob += (
        lpSum(
            [(recipe_dict["vitamin_B12"][recipe] +
              recipe_dict["vitamin_B12_added"]
              [recipe])
             * recipe_var[recipe] for recipe
             in recipes]) >= micros["vit_b12_ug_rda"],
        "Minvitamin_b12_(ug)Requirement",
    )

    prob += (
        lpSum(
            [(recipe_dict["vitamin_B12"][recipe])
             * recipe_var[recipe] for recipe
             in recipes]) <= micros["vit_b12_ug_ul"],
        "Maxvitamin_b12_(ug)Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["folate_total"][recipe] * recipe_var[recipe] for recipe
             in recipes]) <= micros["vit_b9_folate_ug_ul"],
        "Maxfolate_(ug)Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["folate_total"][recipe] * recipe_var[recipe] for recipe
             in recipes]) >= micros["vit_b9_folate_ug_rda"],
        "Minfolate_(ug)Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["vitamin_C"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= micros["vit_c_mg_ul"],
        "Maxvitamin_c_(mg)Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["vitamin_C"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= micros["vit_c_mg_rda"],
        "Minvitamin_c_(mg)Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["vitamin_D"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= micros["vit_d_iu_ul"],
        "Maxvitamin_d_(iu)Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["vitamin_D"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= micros["vit_d_iu_ai"],
        "Minvitamin_d_(iu)Requirement",
    )

    prob += (
        lpSum(
            [(recipe_dict["vitamin_E"][recipe])
             * recipe_var[recipe] for recipe in
             recipes]) <= micros["vit_e_mg_ul"],
        "Maxvitamin_e_(mg)Requirement",
    )

    prob += (
        lpSum(
            [(recipe_dict["vitamin_E"][recipe] )
             * recipe_var[recipe] for recipe in
             recipes]) >= micros["vit_e_mg_rda"],
        "Minvitamin_e_(mg)Requirement",
    )

    prob += (
        lpSum([recipe_dict["choline"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= micros["vit_choline_mg_ai"],
        "Mincholine_(mg)Requirement",
    )

    prob += (
        lpSum([recipe_dict["choline"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= micros["vit_choline_mg_ul"],
        "Maxcholine_(mg)Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["vitamin_K"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= micros["vit_k_ug_ul"],
        "Maxvitamin_k_(ug)Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["vitamin_K"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= micros["vit_k_ug_ai"],
        "Minvitamin_k_(ug)Requirement",
    )

    """
    Below are the absolute constraints. These constraints are in the same form
    as the other constraints but have a different real world meaning. The
    purpose of them are to fine tune the results to give values that we want
    less about fitting a mealplan into a diet.
    """
    prob += lpSum([recipe_var[i] for i in recipes]) <= 11 * days

    #restrict the number of recipes that can be selected
    prob += lpSum([recipe_var[int(i)] for i in exclude]) == 0

    #force inclusion of recipe
    prob += lpSum([recipe_var[int(i)] for i in include]) >= len(include)

    CALORIE_CAP = 400
    MIN_CALORIE_CAP = 100
    # Ensures that a recipe is not selected more than a certain amount of times, can be changed
    for recipe in recipes:
        calories = recipe_df.loc[recipe_df['number'] == recipe]["energy_kcal"].values
        if calories and calories[0] < CALORIE_CAP  and calories[0] > MIN_CALORIE_CAP:
            recipe_limit = int(CALORIE_CAP / calories[0])
        else:
            recipe_limit = 1
        prob += recipe_var[recipe] <= recipe_limit

    # The problem data is written to an .lp file

    # The problem is solved using PuLP's choice of Solver, the input
    # is so messages are no longer displayd
    prob.solve(PULP_CBC_CMD(msg=0))

    result = {}
    result["constraints_loosened"] = False
    """
    Repeat solving with loosened constraints if infeasible not implmented yet a
    last resort measure
    """
    #used in the event  we need to loosen constraints
    original_constraints = None

    if LpStatus[prob.status] == LpStatus[LpStatusInfeasible]:
        print("Problem is infeasible, attempting to solve with loosened constraints")
        print("Original Constraints")
        result["constraints_loosened"] = True

        orig_constraints = print_soln_constraints(prob.constraints)

        max_change_factor = 10
        current_change_factor = 1

        #keep on looping until optimal is found, or until we have loosened the constraints by a factor of 10
        #factor of 10 is arbitrary and right now done to stop infinite loops as if we increase other nutrients by
        #a factor of 10, and still have infeasible, the problem may be somewhere else.
        while LpStatus[prob.status] == LpStatus[LpStatusInfeasible] and current_change_factor < max_change_factor:
            prob = solveWithLoosenedConstraints(prob, constraint_relaxation, excluded_nutrients)
            current_change_factor += constraint_relaxation

        print("Solved for meal plan with loosened constraints")

    recipe_name_quant = []
    for v in prob.variables():
        if v.varValue is not None and v.varValue > 0 :
            recipe_id = v.name[8:]
            recipe_name = recipe_df.loc[recipe_df['number'] == int(recipe_id)]['title'].values[0]
            recipe_name_quant.append({'name': f"{recipe_name}",
                                    'multiples': v.varValue})

            print(recipe_name, "=", v.varValue)

    result["recipes"] = recipe_name_quant
    result["status"] = LpStatus[prob.status]
    print("\n")

    constraint_results = print_soln_constraints(prob.constraints)

    if orig_constraints is not None:
        result["out_of_orig_bound_nutrients"] = print_constraint_differences(orig_constraints, constraint_results)
        constraint_results = combine_orig_constraints(orig_constraints, constraint_results)

    # The optimised objective function value is printed to the screen
    print("Maximum Meal Plan Value = ", value(prob.objective))

    # The status of the solution is printed to the screen
    print("Status:", LpStatus[prob.status])

    result["constraint_targets"] = constraint_results
    return result

def combine_orig_constraints(orig, current):
    """
    Combines the original constraints from the original problem with the
    values from the problem after the constraints have been loosened.
    """
    for index in range(len(orig)):
        current[index]["target"] = orig[index]["target"]

    return current
def print_constraint_differences(orig, current):
    """
    Given output from print_soln_constraints with the original values and current
    values shows the difference between the two. Shows what nutrients are out of
    bounds in the current when compared to the
    """
    out_of_range_nutrients = []
    for index in range(len(orig)):
        orig_nutrient_name = orig[index]["name"]
        orig_nutrient_min = int(orig[index]["target"].split("-")[0])
        if orig[index]["target"].split("-")[1] == " ":
            orig_nutrient_max = (2 ** 31) - 1
        else:
            orig_nutrient_max = int(orig[index]["target"].split("-")[1])
        curr_nutrient_value = current[index]["actual"]

        if curr_nutrient_value < orig_nutrient_min:
            out_of_range_nutrients.append(orig_nutrient_name)
            print(f"{orig_nutrient_name} is lower than original {orig_nutrient_min}: curr value {curr_nutrient_value}")
        elif curr_nutrient_value > orig_nutrient_max:
            out_of_range_nutrients.append(orig_nutrient_name)
            print(f"{orig_nutrient_name} is higher than original {orig_nutrient_max}: curr value {curr_nutrient_value}")

    return out_of_range_nutrients

def solveWithLoosenedConstraints(prob, scale, excluded = []):
    """
    Given an already defined pulp problem who's status is infeasible, try to
    loosen the constraints and try again.

    :param prob: The problem to solve
    :param scale: Amount to scale the bounds by
    :param excluded: List of nutrients to exclude from loosening
    :return: The problem after it has been solved
    """
    GENERAL_EXCLUDED_NUTRIENTS = ["energy", "sodium", "fats"]

    for constraint in prob.constraints:
        if prob.constraints[constraint].name is not None:
            # get name of the nutrient. Constraint has naming convention
            # Min<constraint_name>Requirement or Max<constraint_name>Requirement
            nutrient_name = prob.constraints[constraint].name[3:-11].lower().replace("_", " ")
            nutrient_name = nutrient_name.rsplit(" ", 1)[0]

            if nutrient_name in excluded or nutrient_name in GENERAL_EXCLUDED_NUTRIENTS:
                continue
            else:
                upper_bound = prob.constraints[constraint].getUb()
                lower_bound = prob.constraints[constraint].getLb()

                if lower_bound != None:
                    new_value = lower_bound * (1 - scale)
                if upper_bound != None:
                    new_value = upper_bound * (1 + scale)

                prob.constraints[constraint].changeRHS(new_value)

    prob.solve(PULP_CBC_CMD(msg=0))

    return prob

def rreplace(s, old, new, occurrence):
    """
    Replaces the rightmost old values in a string with the new values, occurence
    number of times

    s
    '1232425'
    rreplace(s, '2', ' ', 2)
    '123 4 5'
    rreplace(s, '2', ' ', 3)
    '1 3 4 5'
    rreplace(s, '2', ' ', 4)
    '1 3 4 5'
    rreplace(s, '2', ' ', 0)
    '1232425'
    """

    li = s.rsplit(old, occurrence)
    return new.join(li)

def print_soln_constraints(constraints):
    """
    Prints the values for each constraint after it has been solved for in an
    lp problem. It is assumed the constraint names take on the form of

    Min<constraint_name>Requirement
    Max<constraint_name>Requirement
    <constraint_name>Requirement

    :param constraints: The constraints from the LP problem, after everything
    is added. If your problem variable is called prob, then it would be
    prob.constraints
    """

    # Constants used to adjust spacing when formatting the output

    TEXT_SPACING = 20
    DECIMAL_PLACES = 0
    DIVIDER_AMOUNT = 105
    SUFFIX_LEN = 11
    PREFIX_LEN = 3

    prior_name = None

    print(f"{'Requirement':{TEXT_SPACING}s} {'Solved Value':>{TEXT_SPACING}s}"
          f"{'Lower Bound':>{TEXT_SPACING}s} {'Upper Bound':>{TEXT_SPACING}s}"
          f"{'Bounds Error':>{TEXT_SPACING}s}")
    print("=" * DIVIDER_AMOUNT)

    constraint_result = []

    for constraint in constraints:
        if constraints[constraint].name is not None:
            constraint_name = constraints[constraint].name.lower()

            # get the name of the string without min/max and requirement in the name
            if "max" in constraint_name or "min" in constraint_name:
                current_name_stripped = constraint_name[PREFIX_LEN:-SUFFIX_LEN]
            else:
                current_name_stripped = constraint_name[:-SUFFIX_LEN]

            if prior_name is None or current_name_stripped != prior_name:
                prior_name = current_name_stripped
                bounds_dict = getConstraintBounds(constraints,
                                                  current_name_stripped)

                constraint_sum = constraints[constraint].value() - constraints[
                    constraint].constant

                bounds_error = checkConstraintBounds(bounds_dict['lower'],
                                                     bounds_dict['upper'])
                lower = f"{bounds_dict['lower']}"
                if bounds_dict['upper'] >= (2 ** 31) - 1:
                    upper = ""
                else:
                    upper = f"{bounds_dict['upper']}"

                print(f"{current_name_stripped.replace('_', ' '):{TEXT_SPACING}s} "
                      f"{constraint_sum:{TEXT_SPACING}.{DECIMAL_PLACES}f}"
                      f"{lower:>{TEXT_SPACING}s}"
                      f"{upper:>{TEXT_SPACING}s}"
                      f"{bounds_error:>{TEXT_SPACING}s}")
                constraint_result.append({"actual": int(constraint_sum),
                                          "name": rreplace(current_name_stripped, "_", " ", 1),
                                          "target": f"{lower} - {upper}"})
    print("\n")
    return constraint_result


def checkConstraintBounds(lower, upper):
    """
    Checks if the lower and upper bounds of a constraint are valid and returns
    the appropriate error string.
    """

    if lower != None and upper != None:
        if lower > upper:
            return "Error!"

    return ''


def getConstraintBounds(constraints, constraint_name):
    """
    Given a constraint name and dictionary of constraints, finds the bounds of
    that constraint. This is assuming the constraint can potentially have an
    upper and lower bound, and that the constraint name takes on the form of
    Max/Min <constraint_name> Requirement or <constraint_name> Requirement

    :param constraints: dictionary of constraints that we are looking through
    :param constraint_name: name of the constraint we want the bounds for,
    this is assuming the constraint name takes on the form of <constraint_name>
    and not Max/Min <constraint_name> requirement

    :return: Dictionary with keys upper and lower, that contain the upper and
    lower bounds of the constraint
    """
    MAX_PREFIX = "Max"
    MIN_PREFIX = "Min"
    SUFFIX = "Requirement"

    result_dict = {"upper": None, "lower": 0}
    const_suffix = constraint_name + SUFFIX
    if MAX_PREFIX + const_suffix in constraints:
        result_dict["upper"] = int(
            constraints[MAX_PREFIX + const_suffix].getUb())

    if MIN_PREFIX + const_suffix in constraints:
        result_dict["lower"] = int(
            constraints[MIN_PREFIX + const_suffix].getLb())

    if const_suffix in constraints:
        upper_bound = constraints[const_suffix].getUb()
        lower_bound = constraints[const_suffix].getLb()
        result_dict["upper"] = result_dict[
            "upper"] if upper_bound == None else int(upper_bound)
        result_dict["lower"] = result_dict[
            "lower"] if lower_bound == None else int(lower_bound)

    return result_dict


def modifyUserConstraintsByDays(days, constraints):
    user_constraints = {}
    for key, value in constraints.items():
        if type(value) == list:
            user_constraints[key] = [x * days for x in value]
        elif not isinstance(value, str):
            user_constraints[key] = value * days
        else:
            user_constraints[key] = value

    return user_constraints
