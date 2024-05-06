"""
This file contains methods used to generate or help generate an optimal meal
plan for a given set of constraints. These constraints are to be passed into the
methods used for the generation of the meal plans. A meal plan refers to a list
of recipes that that cover breakfast, lunch and dinner over a 1 week period.
Ideally the output should give 21 recipes.

In this instance constraints refers to nutritional needs such as calories,
sodium, fat requirements or other needs such as having 1 breakfast, 1 lunch,
and 1 dinner for a day.

NOTE:
    a lot of comments in this file will be removed later on as things get
    clarified. Explanations will be more succinct and there will be less
    uncertainty
"""
from pulp import *
import pandas as pd
import json

MEAL_DATABASE_PATH = "meal_database_4.csv"
DIET_DATABASE_PATH = "DietUSDA_5.csv"

# These constants are for finding ranges for hard set values such as Calories.
# eating 2088 calories exact is hard so we take +- 5%
LOWER_RANGE = 0.95
UPPER_RANGE = 1.05


@staticmethod
def getRecipeList():
    """
    Currently used for generating dummy data will be removed later
    """
    df = pd.read_csv(MEAL_DATABASE_PATH)
    recipes = list(df["title"])
    return recipes


@staticmethod
def getFakeUserPref():
    """
    Currently used for generating dummy data will be removed later
    """
    recipes = getRecipeList()
    user_pref = dict(zip(recipes, [1 for recipe in recipes]))
    return user_pref


@staticmethod
def getFromDatabase():
    """
    Currently used for generating data from the database, will either be
    removed or potentially modified later.
    """
    df = pd.read_csv(MEAL_DATABASE_PATH)
    df = df.drop(columns=['ingredients_with_quantities', 'cooking instructions'])
    df = df.dropna()
    nutrient_dict = {}
    recipes = list(df["title"])
    nutrient_dict["number"] = dict(zip(recipes, df["number"]))
    nutrient_dict["meal_type"] = dict(zip(recipes, df["meal_type"]))
    nutrient_dict["meal_slot"] = dict(zip(recipes, df["meal_slot"]))
    nutrient_dict["title"] = recipes
    nutrient_dict["Calories"] = dict(zip(recipes, df["energy_kcal"]))
    nutrient_dict["kj"] = dict(zip(recipes, df["energy_kj"]))
    nutrient_dict["fibre"] = dict(zip(recipes, df["fibre_g"]))
    nutrient_dict["carbohydrates"] = dict(zip(recipes, df["carbohydrates_g"]))
    nutrient_dict["starch"] = dict(zip(recipes, df["starch_g"]))
    nutrient_dict["cholesterol"] = dict(zip(recipes, df["cholesterol_mg"]))
    nutrient_dict["sugar"] = dict(zip(recipes, df["sugars_total_g"]))
    nutrient_dict["water"] = dict(zip(recipes, df["water_g"]))
    nutrient_dict["protein"] = dict(zip(recipes, df["protein_g"]))
    nutrient_dict["fats_total"] = dict(zip(recipes, df["fats_total_g"]))
    nutrient_dict["trans_fats"] = dict(
        zip(recipes, df["fatty_acids_total_trans_g"]))
    nutrient_dict["vitamin_A"] = dict(
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


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def getFakeConstraints():
    df = pd.read_csv(DIET_DATABASE_PATH)
    constraints = df.iloc[6].to_dict()
    constraints["Calories"] = 2088
    constraints["max_fibre"] = 60
    constraints["min_fibre"] = 50
    constraints["starch"] = 0
    constraints["sugar"] = 36
    constraints["protein"] = 55
    constraints["max_fats_total"] = 78
    constraints["min_fats_total"] = 44
    constraints["trans_fats"] = 2.2
    constraints["min_carbohydrates"] = 225
    constraints["max_carbohydrates"] = 325
    constraints["cholesterol"] = 300
    user_constraints = {}

    for key, value in constraints.items():
        if value == "ND":
            if "ul" in key:
                new_key = key.replace("ul", "rda")
                if key in constraints:
                    user_constraints[key] = 10000000

                new_key = key.replace("ul", "ai")
                if key in constraints:
                    user_constraints[key] = 10000000
            else:
                user_constraints[key] = 0
        else:
            if isinstance(value, str) and isfloat(value):
                user_constraints[key] = float(value)
            else:
                user_constraints[key] = value

    return user_constraints

def get_recipe_dict_from_df(recipe_df):
    """
    Currently used for generating data from the database, will either be
    removed or potentially modified later.
    """
    df = recipe_df
    df = df.drop(columns=['ingredients_with_quantities', 'cooking instructions'])
    df = df.dropna()
    nutrient_dict = {}
    recipes = list(df["title"])
    nutrient_dict["user_score"] = dict(zip(recipes, df["score"]))
    nutrient_dict["number"] = dict(zip(recipes, df["number"]))
    nutrient_dict["meal_type"] = dict(zip(recipes, df["meal_type"]))
    nutrient_dict["meal_slot"] = dict(zip(recipes, df["meal_slot"]))
    nutrient_dict["title"] = recipes
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
    nutrient_dict["choline"] = dict(zip(recipes, df["choline_g"]))
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


@staticmethod
def optimize_meals_integration(recipe_df, macros, micros,user_score, user_diet, days= 1 , exclude=[], include=[]):
    """
    integration of optimize meal with arjun's code, will be deleted later and
    merged into optimize_meals
    """
    #Indexes for minimum/maximum values for macros
    MIN_INDEX = 0
    MAX_INDEX = 1

    #Process Recipes dataframe
    recipe_dict = get_recipe_dict_from_df(recipe_df)

    #Update micros and macros to number of days
    micros = modifyUserConstraintsByDays(days, micros)
    macros = modifyUserConstraintsByDays(days, macros)

    #Create user ref and diet

    recipes = recipe_dict["title"]

    prob = LpProblem("Meal plan generation", LpMaximize)

    recipe_var = LpVariable.dicts("Recipes", recipes, lowBound=0,
                                  cat='Integer')

# recipe_dict["user_score"][i]
    prob += lpSum(
        [recipe_var[i] * recipe_dict["user_score"][i] * user_diet[i] for i in recipes])


    prob += (
        lpSum(
            [recipe_dict["Calories"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= macros["large_calories"] * UPPER_RANGE,
        "MaxcaloriesRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["Calories"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= (macros["large_calories"] * LOWER_RANGE),
        "MincaloriesRequirement",
    )

    prob += (
        lpSum([recipe_dict["fibre"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= macros["fiber_g"][MAX_INDEX],
        "MaxfibreRequirement",
    )

    prob += (
        lpSum([recipe_dict["fibre"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= macros["fiber_g"][MIN_INDEX],
        "MinfibreRequirement",
    )

    prob += (
        lpSum([recipe_dict["carbohydrates"][recipe] * recipe_var[recipe] for
               recipe in recipes]) <=  macros["carbohydrates_g"][MAX_INDEX],
        "MaxcarbohydratesRequirement",
    )

    prob += (
        lpSum([recipe_dict["carbohydrates"][recipe] * recipe_var[recipe] for
               recipe in recipes]) >=  macros["carbohydrates_g"][MIN_INDEX],
        "MincarbohydratesRequirement",
    )

    prob += (
        lpSum([recipe_dict["protein"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= macros["protein_g"][MAX_INDEX],
        "MaxproteinRequirement",
    )

    prob += (
        lpSum([recipe_dict["protein"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= macros["protein_g"][MIN_INDEX],
        "MinproteinRequirement",
    )

    prob += (
        lpSum([recipe_dict["fats_total"][recipe] * recipe_var[recipe] for recipe
               in recipes]) <= macros["fat_g"][MAX_INDEX],
        "Maxfats_totalRequirement",
    )

    prob += (
        lpSum([recipe_dict["fats_total"][recipe] * recipe_var[recipe] for recipe
               in recipes]) >= macros["fat_g"][MIN_INDEX],
        "Minfats_totalRequirement",
    )

    # prob += (
    #     lpSum([recipe_dict["trans_fats"][recipe] * recipe_var[recipe] for recipe
    #            in recipes]) <= constraints["trans_fats"],
    #     "trans_fatsRequirement",
    # )

    """
    Micros
    """

    prob += (
        lpSum([recipe_dict["calcium"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= micros["min_calcium_mg_ul"],
        "MaxcalciumRequirement",
    )

    prob += (
        lpSum([recipe_dict["calcium"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= micros["min_calcium_mg_ai"],
        "MincalciumRequirement",
    )
    #
    prob += (
        lpSum([recipe_dict["sodium"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= (micros["min_sodium_mg_ul"]),
        "MaxsodiumRequirement",
    )

    prob += (
        lpSum([recipe_dict["sodium"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= (micros["min_sodium_mg_ai"]),
        "MinsodiumRequirement",
    )
    #
    prob += (
        lpSum([recipe_dict["copper"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= micros["min_copper_mg_rda"],
        "MincopperRequirement",
    )

    prob += (
        lpSum([recipe_dict["copper"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= micros["min_copper_mg_ul"],
        "MaxcopperRequirement",
    )
    #
    prob += (
        lpSum(
            [recipe_dict["flouride"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= micros["min_fluoride_mg_ai"],
        "MinflourideRequirement",
    )
    #
    prob += (
        lpSum(
            [recipe_dict["flouride"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= micros["min_fluoride_mg_ul"],
        "MaxflourideRequirement",
    )

    prob += (
        lpSum([recipe_dict["iron"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= micros["min_iron_mg_rda"],
        "MinironRequirement",
    )

    prob += (
        lpSum([recipe_dict["iron"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= micros["min_iron_mg_ul"],
        "MaxironRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["magnesium"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= micros["min_magnesium_mg_ul"],
        "MaxmagnesiumRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["magnesium"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= micros["min_magnesium_mg_rda"],
        "MinmagnesiumRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["manganese"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= micros["min_manganese_mg_ul"],
        "MaxmanganeseRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["manganese"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= micros["min_manganese_mg_rda"],
        "MinmanganeseRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["potassium"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= micros["min_potassium_mg_ai"],
        "MinpotassiumRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["potassium"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= micros["min_potassium_ul"],
        "MaxpotassiumRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["selenium"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= micros["min_selenium_ug_ul"],
        "MaxseleniumRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["selenium"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= micros["min_selenium_ug_rda"],
        "MinseleniumRequirement",
    )

    prob += (
        lpSum([recipe_dict["zinc"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= micros["min_zinc_mg_rda"],
        "MinzincRequirement",
    )

    prob += (
        lpSum([recipe_dict["zinc"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= micros["min_zinc_mg_ul"],
        "MaxzincRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["vitamin_A"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= micros["vit_a_ug_ul"],
        "Maxvitamin_aRequirement",
    )
    prob += (
        lpSum(
            [recipe_dict["vitamin_A"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= micros["vit_a_ug_rda"],
        "Minvitamin_aRequirement",
    )

    prob += (
        lpSum([recipe_dict["thiamin"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= micros["vit_b1_thiamin_mg_ul"],
        "MaxthiaminRequirement",
    )

    prob += (
        lpSum([recipe_dict["thiamin"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= micros["vit_b1_thiamin_mg_rda"],
        "MinthiaminRequirement",
    )

    prob += (
        lpSum([recipe_dict["riboflavin"][recipe] * recipe_var[recipe] for recipe
               in recipes]) <= micros["vit_b2_riboflavin_mg_ul"],
        "MaxriboflavinRequirement",
    )

    prob += (
        lpSum([recipe_dict["riboflavin"][recipe] * recipe_var[recipe] for recipe
               in recipes]) >= micros["vit_b2_riboflavin_mg_rda"],
        "MinriboflavinRequirement",
    )

    prob += (
        lpSum([recipe_dict["niacin"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= micros["vit_b3_niacin_mg_ul"],
        "MaxniacinRequirement",
    )

    prob += (
        lpSum([recipe_dict["niacin"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= micros["vit_b3_niacin_mg_rda"],
        "MinniacinRequirement",
    )

    prob += (
        lpSum([recipe_dict["vitamin_B5"][recipe] * recipe_var[recipe] for recipe
               in recipes]) <= micros["vit_b5_pantothenic_acid_mg_ul"],
        "Maxvitamin_b5Requirement",
    )

    prob += (
        lpSum([recipe_dict["vitamin_B5"][recipe] * recipe_var[recipe] for recipe
               in recipes]) >= micros["vit_b5_pantothenicacid_mg_ai"],
        "Minvitamin_b5Requirement",
    )

    prob += (
        lpSum([recipe_dict["vitamin_B6"][recipe] * recipe_var[recipe] for recipe
               in recipes]) <= micros["vit_b6_mg_ul"],
        "Maxvitamin_b6Requirement",
    )

    prob += (
        lpSum([recipe_dict["vitamin_B6"][recipe] * recipe_var[recipe] for recipe
               in recipes]) >= micros["vit_b6_mg_rda"],
        "Minvitamin_b6Requirement",
    )

    prob += (
        lpSum(
            [(recipe_dict["vitamin_B12"][recipe] +
              recipe_dict["vitamin_B12_added"]
              [recipe])
             * recipe_var[recipe] for recipe
             in recipes]) >= micros["vit_b12_ug_rda"],
        "Minvitamin_b12Requirement",
    )

    prob += (
        lpSum(
            [(recipe_dict["vitamin_B12"][recipe] +
              recipe_dict["vitamin_B12_added"]
              [recipe])
             * recipe_var[recipe] for recipe
             in recipes]) <= micros["vit_b12_ug_ul"],
        "Maxvitamin_b12Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["folate_total"][recipe] * recipe_var[recipe] for recipe
             in recipes]) <= micros["vit_b9_folate_ug_ul"],
        "Maxfolate_totalRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["folate_total"][recipe] * recipe_var[recipe] for recipe
             in recipes]) >= micros["vit_b9_folate_ug_rda"],
        "Minfolate_totalRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["vitamin_C"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= micros["vit_c_mg_ul"],
        "Maxvitamin_cRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["vitamin_C"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= micros["vit_c_mg_rda"],
        "Minvitamin_cRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["vitamin_D"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= micros["vit_d_ug_ul"],
        "Maxvitamin_dRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["vitamin_D"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= micros["vit_d_ug_ai"],
        "Minvitamin_dRequirement",
    )

    # prob += (
    #     lpSum(
    #         [(recipe_dict["vitamin_E"][recipe] + recipe_dict["vitamin_E_added"]
    #           [recipe])
    #          * recipe_var[recipe] for recipe in
    #          recipes]) <= micros["vit_e_mg_ul"],
    #     "Maxvitamin_eRequirement",
    # )
    #
    # prob += (
    #     lpSum(
    #         [(recipe_dict["vitamin_E"][recipe] + recipe_dict["vitamin_E_added"]
    #           [recipe])
    #          * recipe_var[recipe] for recipe in
    #          recipes]) >= micros["vit_e_mg_rda"],
    #     "Minvitamin_eRequirement",
    # )

    # prob += (
    #     lpSum([recipe_dict["choline"][recipe] * recipe_var[recipe] for recipe in
    #            recipes]) >= micros["vit_choline_mg_ai"],
    #     "MincholineRequirement",
    # )
    #
    # prob += (
    #     lpSum([recipe_dict["choline"][recipe] * recipe_var[recipe] for recipe in
    #            recipes]) <= micros["vit_choline_mg_ul"],
    #     "MaxcholineRequirement",
    # )
    #
    prob += (
        lpSum(
            [recipe_dict["vitamin_K"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= micros["vit_k_ug_ul"],
        "Maxvitamin_kRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["vitamin_K"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= micros["vit_k_ug_ai"],
        "Minvitamin_kRequirement",
    )


    """
    Below are the absolute constraints. These constraints are in the same form
    as the other constraints but have a different real world meaning. The
    purpose of them are to fine tune the results to give values that we want
    less about fitting a mealplan into a diet.
    """

    # generate 21 servings of meals
    #
    prob += lpSum([recipe_var[i] for i in recipes]) <= 3 * days

    #restrict the number of recipes that can be selected

    prob += lpSum([recipe_var[i] for i in exclude]) == 0

    #force inclusion of recipe
    prob += lpSum([recipe_var[i] for i in include]) >= len(include)

    # Ensures that a recipe is not selected more than once, can be changed
    # by adjusting the int
    for recipe in recipes:
        prob += recipe_var[recipe] <= 1

    # The problem data is written to an .lp file
    prob.writeLP("FindMeals.lp")

    # The problem is solved using PuLP's choice of Solver, the input
    # is so messages are no longer displayd
    prob.solve(PULP_CBC_CMD(msg=0))

    """
    Repeat solving with loosened constraints if infeasible
    """
    # if LpStatus[prob.status] == LpStatus[LpStatusInfeasible]:
    #     print("Problem is infeasible, attempting to solve with loosened constraints")
    #     print("Original Constraints")
    #     print_soln_constraints(prob.constraints)
    #
    #     while LpStatus[prob.status] == LpStatus[LpStatusInfeasible]:
    #         prob = solveWithLoosenedConstraints(prob, 0.05)
    #
    #     print("Solved for meal plan with loosened constraints")

    # Each of the variables is printed with it's resolved optimum value
    for v in prob.variables():
        if v.varValue > 0:
            print(v.name, "=", v.varValue)

    print("\n")

    print_soln_constraints(prob.constraints)

    # The optimised objective function value is printed to the screen
    print("Maximum Meal Plan Value = ", value(prob.objective))

    # The status of the solution is printed to the screen
    print("Status:", LpStatus[prob.status])





@staticmethod
def optimize_meals(recipe_dict, constraints, user_diet, user_pref, days=1, exclude = [], include = []):
    """
    WILL REWRITE THIS COMMENT WHEN MORE FINISHED

    This function aims to find an optimal meal plan given the inputs. An
    objective function is ran using the recipes and constraints given which
    attempts to solve for the meal plan that has the greatest value. Value in
    this instant refers to meals that best fit the constraints given.

    :param recipes: a list of recipes that are to be evaluated to create a
    proper meal

    Right now unsure of what form recipes take. The information I need from
    recipes is, nutrient content, user preferences (likes dislikes),

    :param constraints: A dictionary containing the nutritional needs to be
    solved for. I.e total of all meals can't be more than 10 000 calories, has
    between 5 and 50 g of fat. These

    :param user_diet: a bit unsure for this param, but most likely will be
    the dietary needs of the user that can be compared to the dietary needs
    met by the recipe.

    :return: an array of dictionaries where each dictionary specifies the
    breakfast, lunch and dinner for a day
    """
    recipes = recipe_dict["title"]

    prob = LpProblem("Meal plan generation", LpMaximize)

    """
    The following line takes the recipe titles and puts them into a dictionary 
    where key is recipe name, and value is the variable itself 
    """
    recipe_var = LpVariable.dicts("Recipes", recipes, lowBound=0,
                                  cat='Integer')

    """
    The following function is the objective function. It refers to the 
    function we are trying to maximize. The code is not intuitive upon first 
    glance, but the objective function is 

    value = (X1 * fit_to diet * fit_to_pref  + X2 * fit_to_diet * fit_to_pref + .... 
    + Xn * fit_to_diet * fit_to_pref)

    Where 
        fit_to_pref:
            include hard constraints as religious constraints and allergy 
            constraints among other regular preferences such as likes and 
            dislikes
            
        fit_to_diet:
            a score for how well the recipe fits the diet. For example a croissant
            would have a low score for a low fat diet, but a higher score for
            a normal fat diet.
        Xn:
            Refers to the recipe itself. These are the decision variables
            and are what pulp attempts to decide how much of each variable
            we have
    
    Essentially using this function we are trying to find the values of 
    X1,X2,X3 ... Xn that will give us the maximum possible value.
    
    In plain english this means we are trying to find a mealplan that best
    fits the user based off of their preferences and diet
    """

    prob += lpSum(
        [recipe_var[i] * user_pref[i] * user_diet[i] for i in recipes])

    """
    Below are the nutrient constraints, these look similair to the objective 
    function as seen below
    
    (X1 * nutrient_value_for_recipe  + X2 * nutrient_value_for_recipe .... 
    + Xn * nutrient_value_for_recipe ) COMPARATOR nutrition_constraint
    
    where 
        nutrient_value_for_recipe:
        is the amount of the nutrient the recipe contains. I.e X1 * calories
        
        COPMARATOR:
        A comparator such as ==, < , > , <= , >=. The purpose of this is
        to compare the value obtained with the constraint
        
        nutrition_constraint:
        the bounds the value must be constrained by. i.e if we are talking about
        a 5ft 10 25yo male that wants to maintain a weight of 165 lbs and is
        sedentary  they would need 2088 calories per day. Setting this as an
        exact constraint however is quite strict, so 
        
    The purpose of these constraints are to provide extra bounds on the 
    objective function. So while the objective function is being maximized
    these constraints must always be met.
    
    In plain english these constraints are made so a mealplan that goes over
    the reccomended nutrient amounts for the diet is not returned. 
    
    I.e 
    Even though someone may love having a mealplan full of donuts and cake, 
    that would go way over the Calorie limit and shouldn't be made in the first 
    place.
    
    COMMENTED OUT CODE IS FOR NUTRIENTS I'M UNSURE ABOUT
    """

    calorie_upper_constraint = constraints["Calories"] * UPPER_RANGE

    prob += (
        lpSum(
            [recipe_dict["Calories"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= calorie_upper_constraint,
        "MaxcaloriesRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["Calories"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= (constraints["Calories"] * LOWER_RANGE),
        "MincaloriesRequirement",
    )

    prob += (
        lpSum([recipe_dict["fibre"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= constraints["max_fibre"],
        "MaxfibreRequirement",
    )

    prob += (
        lpSum([recipe_dict["fibre"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= constraints["min_fibre"],
        "MinfibreRequirement",
    )

    prob += (
        lpSum([recipe_dict["carbohydrates"][recipe] * recipe_var[recipe] for
               recipe in recipes]) <= constraints["max_carbohydrates"],
        "MaxcarbohydratesRequirement",
    )

    prob += (
        lpSum([recipe_dict["carbohydrates"][recipe] * recipe_var[recipe] for
               recipe in recipes]) >= constraints["min_carbohydrates"],
        "MincarbohydratesRequirement",
    )

    prob += (
        lpSum([recipe_dict["protein"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= constraints["protein"],
        "proteinRequirement",
    )

    prob += (
        lpSum([recipe_dict["fats_total"][recipe] * recipe_var[recipe] for recipe
               in recipes]) <= constraints["max_fats_total"],
        "Maxfats_totalRequirement",
    )

    prob += (
        lpSum([recipe_dict["fats_total"][recipe] * recipe_var[recipe] for recipe
               in recipes]) >= constraints["min_fats_total"],
        "Minfats_totalRequirement",
    )


    # """
    # Micros
    # """
    #
    prob += (
        lpSum([recipe_dict["calcium"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= constraints["min_calcium_mg_ul"],
        "MaxcalciumRequirement",
    )

    prob += (
        lpSum([recipe_dict["calcium"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= constraints["min_calcium_mg_ai"],
        "MincalciumRequirement",
    )
    #
    prob += (
        lpSum([recipe_dict["sodium"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= (constraints["min_sodium_mg_ul"] ),
        "MaxsodiumRequirement",
    )

    prob += (
        lpSum([recipe_dict["sodium"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= (constraints["min_sodium_mg_ai"] ),
        "MinsodiumRequirement",
    )
    #
    prob += (
        lpSum([recipe_dict["copper"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= constraints["min_copper_mg_rda"],
        "MincopperRequirement",
    )

    prob += (
        lpSum([recipe_dict["copper"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= constraints["min_copper_mg_ul"],
        "MaxcopperRequirement",
    )
    #
    prob += (
        lpSum(
            [recipe_dict["flouride"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= constraints["min_fluoride_mg_ai"],
        "MinflourideRequirement",
    )
    #
    prob += (
        lpSum(
            [recipe_dict["flouride"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= constraints["min_fluoride_mg_ul"],
        "MaxflourideRequirement",
    )

    prob += (
        lpSum([recipe_dict["iron"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= constraints["min_iron_mg_rda"],
        "MinironRequirement",
    )

    prob += (
        lpSum([recipe_dict["iron"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= constraints["min_iron_mg_ul"],
        "MaxironRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["magnesium"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= constraints["min_magnesium_mg_ul"],
        "MaxmagnesiumRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["magnesium"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= constraints["min_magnesium_mg_rda"],
        "MinmagnesiumRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["manganese"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= constraints["min_manganese_mg_ul"],
        "MaxmanganeseRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["manganese"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= constraints["min_manganese_mg_rda"],
        "MinmanganeseRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["potassium"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= constraints["min_potassium_mg_ai"],
        "MinpotassiumRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["potassium"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= constraints["min_potassium_ul"],
        "MaxpotassiumRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["selenium"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= constraints["min_selenium_ug_ul"],
        "MaxseleniumRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["selenium"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= constraints["min_selenium_ug_rda"],
        "MinseleniumRequirement",
    )

    prob += (
        lpSum([recipe_dict["zinc"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= constraints["min_zinc_mg_rda"],
        "MinzincRequirement",
    )

    prob += (
        lpSum([recipe_dict["zinc"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= constraints["min_zinc_mg_ul"],
        "MaxzincRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["vitamin_A"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= constraints["vit_a_iu_ul"],
        "Maxvitamin_aRequirement",
    )
    prob += (
        lpSum(
            [recipe_dict["vitamin_A"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= constraints["vit_a_iu_rda"],
        "Minvitamin_aRequirement",
    )

    prob += (
        lpSum([recipe_dict["thiamin"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= constraints["vit_b1_thiamin_mg_ul"],
        "MaxthiaminRequirement",
    )

    prob += (
        lpSum([recipe_dict["thiamin"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= constraints["vit_b1_thiamin_mg_rda"],
        "MinthiaminRequirement",
    )

    prob += (
        lpSum([recipe_dict["riboflavin"][recipe] * recipe_var[recipe] for recipe
               in recipes]) <= constraints["vit_b2_riboflavin_mg_ul"],
        "MaxriboflavinRequirement",
    )

    prob += (
        lpSum([recipe_dict["riboflavin"][recipe] * recipe_var[recipe] for recipe
               in recipes]) >= constraints["vit_b2_riboflavin_mg_rda"],
        "MinriboflavinRequirement",
    )

    prob += (
        lpSum([recipe_dict["niacin"][recipe] * recipe_var[recipe] for recipe in
               recipes]) <= constraints["vit_b3_niacin_mg_ul"],
        "MaxniacinRequirement",
    )

    prob += (
        lpSum([recipe_dict["niacin"][recipe] * recipe_var[recipe] for recipe in
               recipes]) >= constraints["vit_b3_niacin_mg_rda"],
        "MinniacinRequirement",
    )

    prob += (
        lpSum([recipe_dict["vitamin_B5"][recipe] * recipe_var[recipe] for recipe
               in recipes]) <= constraints["vit_b5_pantothenic_acid_mg_ul"],
        "Maxvitamin_b5Requirement",
    )

    prob += (
        lpSum([recipe_dict["vitamin_B5"][recipe] * recipe_var[recipe] for recipe
               in recipes]) >= constraints["vit_b5_pantothenicacid_mg_ai"],
        "Minvitamin_b5Requirement",
    )

    prob += (
        lpSum([recipe_dict["vitamin_B6"][recipe] * recipe_var[recipe] for recipe
               in recipes]) <= constraints["vit_b6_mg_ul"],
        "Maxvitamin_b6Requirement",
    )

    prob += (
        lpSum([recipe_dict["vitamin_B6"][recipe] * recipe_var[recipe] for recipe
               in recipes]) >= constraints["vit_b6_mg_rda"],
        "Minvitamin_b6Requirement",
    )

    prob += (
        lpSum(
            [(recipe_dict["vitamin_B12"][recipe])
             * recipe_var[recipe] for recipe
             in recipes]) >= constraints["vit_b12_ug_rda"],
        "Minvitamin_b12Requirement",
    )

    prob += (
        lpSum(
            [(recipe_dict["vitamin_B12"][recipe] )
             * recipe_var[recipe] for recipe
             in recipes]) <= constraints["vit_b12_ug_ul"],
        "Maxvitamin_b12Requirement",
    )

    prob += (
        lpSum(
            [recipe_dict["folate_total"][recipe] * recipe_var[recipe] for recipe
             in recipes]) <= constraints["vit_b9_folate_ug_ul"],
        "Maxfolate_totalRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["folate_total"][recipe] * recipe_var[recipe] for recipe
             in recipes]) >= constraints["vit_b9_folate_ug_rda"],
        "Minfolate_totalRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["vitamin_C"][recipe] * recipe_var[recipe] for recipe in
             recipes]) <= constraints["vit_c_mg_ul"],
        "Maxvitamin_cRequirement",
    )

    prob += (
        lpSum(
            [recipe_dict["vitamin_C"][recipe] * recipe_var[recipe] for recipe in
             recipes]) >= constraints["vit_c_mg_rda"],
        "Minvitamin_cRequirement",
    )

    # prob += (
    #     lpSum(
    #         [recipe_dict["vitamin_D"][recipe] * recipe_var[recipe] for recipe in
    #          recipes]) <= constraints["vit_d_iu_ul"],
    #     "Maxvitamin_dRequirement",
    # )
    #
    # prob += (
    #     lpSum(
    #         [recipe_dict["vitamin_D"][recipe] * recipe_var[recipe] for recipe in
    #          recipes]) >= constraints["vit_d_iu_ai"],
    #     "Minvitamin_dRequirement",
    # )


    # prob += (
    #     lpSum(
    #         [(recipe_dict["vitamin_E"][recipe] + recipe_dict["vitamin_E_added"]
    #           [recipe])
    #          * recipe_var[recipe] for recipe in
    #          recipes]) <= constraints["vit_e_mg_ul"],
    #     "Maxvitamin_eRequirement",
    # )
    #
    # prob += (
    #     lpSum(
    #         [(recipe_dict["vitamin_E"][recipe] + recipe_dict["vitamin_E_added"]
    #           [recipe])
    #          * recipe_var[recipe] for recipe in
    #          recipes]) >= constraints["vit_e_mg_rda"],
    #     "Minvitamin_eRequirement",
    # )
    #
    #
    # prob += (
    #     lpSum([recipe_dict["choline"][recipe] * recipe_var[recipe] for recipe in
    #            recipes]) >= constraints["vit_choline_mg_ai"],
    #     "MincholineRequirement",
    # )
    #
    # prob += (
    #     lpSum([recipe_dict["choline"][recipe] * recipe_var[recipe] for recipe in
    #            recipes]) <= constraints["vit_choline_mg_ul"],
    #     "MaxcholineRequirement",
    # )
    #
    # prob += (
    #     lpSum(
    #         [recipe_dict["vitamin_K"][recipe] * recipe_var[recipe] for recipe in
    #          recipes]) <= constraints["vit_k_ug_ul"],
    #     "Maxvitamin_kRequirement",
    # )
    #
    # prob += (
    #     lpSum(
    #         [recipe_dict["vitamin_K"][recipe] * recipe_var[recipe] for recipe in
    #          recipes]) >= constraints["vit_k_ug_ai"],
    #     "Minvitamin_kRequirement",
    # )

    #
    # """
    # Below are the absolute constraints. These constraints are in the same form
    # as the other constraints but have a different real world meaning. The
    # purpose of them are to fine tune the results to give values that we want
    # less about fitting a mealplan into a diet.
    # """
    #
    # # not how we want to go about it have to think about it more
    # # # generate 21 servings of meals

    # prob += lpSum([recipe_var[i] for i in recipes]) <= 3 * days

    #print([1 if recipe_var[i].varValue == 0 else 0 for i in recipes])

    #generate 21 meals
    prob += lpSum([recipe_var[i] for i in recipes]) <= 3 * days

    # prob += lpSum([1 if recipe_var[i] != 0 else 0 for i in recipes]) >= 15
    #restrict the number of recipes that can be selected

    prob += lpSum([recipe_var[i] for i in exclude]) == 0

    #force inclusion of recipe
    prob += lpSum([recipe_var[i] for i in include]) >= len(include)

    # Ensures that a recipe is not selected more than once, can be changed
    # by adjusting the int
    # for recipe in recipes:
    #     prob += recipe_var[recipe] <= 3

    # The problem data is written to an .lp file
    prob.writeLP("FindMeals.lp")

    # The problem is solved using PuLP's choice of Solver, the input
    # is so messages are no longer displayd
    prob.solve(PULP_CBC_CMD(msg=0))

    # if LpStatus[prob.status] == LpStatus[LpStatusInfeasible]:
    #     print("Problem is infeasible, attempting to solve with loosened constraints")
    #     print("Original Constraints")
    #     print_soln_constraints(prob.constraints)
    #
    #     while LpStatus[prob.status] == LpStatus[LpStatusInfeasible]:
    #         prob = solveWithLoosenedConstraints(prob, 0.05)
    #
    #     print("Solved for meal plan with loosened constraints")

    # Each of the variables is printed with it's resolved optimum value

    servings = 0
    serving_count = 0
    for v in prob.variables():
        if v.varValue is not None and v.varValue > 0 :
            print(v.name, "=", v.varValue)
            servings = servings + v.varValue
            serving_count = serving_count + 1




    print("\n")

    constraint_values = print_soln_constraints(prob.constraints)
    print("Constraint Values = ", constraint_values)

    # The optimised objective function value is printed to the screen
    print("Maximum Meal Plan Value = ", value(prob.objective))

    # The status of the solution is printed to the screen
    print("Status:", LpStatus[prob.status])
    print("Total Recipes = ", serving_count)
    print("Total Servings = ", servings)


def solveWithLoosenedConstraints(prob, scale):
    """
    Given an already defined pulp problem who's status is infeasible, try to
    loosen the constraints and try again.

    :param scale: Amount to scale the bounds by
    :return: The problem after it has been solved
    """

    for constraint in prob.constraints:
        if prob.constraints[constraint].name is not None:
            upper_bound = prob.constraints[constraint].getUb()
            lower_bound = prob.constraints[constraint].getLb()

            if lower_bound != None:
                new_value = lower_bound * (1- scale)
            if upper_bound != None:
                new_value = upper_bound * (1 + scale)

            prob.constraints[constraint].changeRHS(new_value)

    prob.solve(PULP_CBC_CMD(msg=0))

    return prob


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
    constraint_result = {}
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
                bounds_dict = getConstraintBounds(constraints, current_name_stripped)

                constraint_sum = constraints[constraint].value() - constraints[constraint].constant


                bounds_error = checkConstraintBounds(bounds_dict['lower'], bounds_dict['upper'])
                lower = f"{bounds_dict['lower']}"
                upper = f"{bounds_dict['upper']}"

                constraint_result[current_name_stripped] = {"actual": int(constraint_sum)}
                print(f"{current_name_stripped:{TEXT_SPACING}s} "
                      f"{constraint_sum:{TEXT_SPACING}.{DECIMAL_PLACES}f}"
                      f"{lower:>{TEXT_SPACING}s}"
                      f"{upper:>{TEXT_SPACING}s}"
                      f"{bounds_error:>{TEXT_SPACING}s}")
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
        result_dict["upper"] = int(constraints[MAX_PREFIX + const_suffix].getUb())

    if MIN_PREFIX + const_suffix in constraints:
        result_dict["lower"] = int(constraints[MIN_PREFIX + const_suffix].getLb())


    if const_suffix in constraints:
        upper_bound = constraints[const_suffix].getUb()
        lower_bound = constraints[const_suffix].getLb()
        result_dict["upper"] = result_dict["upper"] if upper_bound == None else int(upper_bound)
        result_dict["lower"] = result_dict["lower"] if lower_bound == None else int(lower_bound)

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


def main():
    # for testing purposes
    days = 7
    nutrition_dict = getFromDatabase()
    user_pref = getFakeUserPref()
    user_diet = getFakeUserPref()
    constraints = getFakeConstraints()
    constraints = modifyUserConstraintsByDays(days, constraints)
    optimize_meals(recipe_dict=nutrition_dict, constraints=constraints,
                   user_diet=user_diet, user_pref=user_pref, days=days,)
    macros = {}
    micros = {}

    # with open('Integration Test\macros.json') as json_file:
    #     macros = json.load(json_file)
    #
    # with open('Integration Test\micros.json') as json_file:
    #     micros = json.load(json_file)
    #
    # recipe_df = pd.read_csv("Integration Test/recipe_with_scores.csv")
    #
    # optimize_meals_integration(recipe_df, macros, micros,user_pref, user_diet, days)


if __name__ == "__main__":
    main()