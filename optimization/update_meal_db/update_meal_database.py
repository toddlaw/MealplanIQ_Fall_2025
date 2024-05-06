"""
The purpose of this file is to update meal_database_1.csv with a diet score
based off of a certain diet. Diets will be found in other CSV's such as
fight_cancer_ingreds_1.csv or fight_cancer_method_1.csv.

The diet score forumula is essentially giving a +2 for every  method it follows
that is preferred, or a -1 for a limit. If the diet says none it is a +1. If
the method or ingredient cannot be found, the score is not affected.
"""

import pandas as pd
import ast
import re


def convertStringToArray(string_array):
    """
    Given a string that represents an array where the contents are all strings
    i.e
    "['beef' ,'chicken' ,'pork' ]"

    returns an actual array representation of the object desired.

    :param string_array: string that represents the array
    :return: an actual array of strings
    """

    try:
        actual_array = ast.literal_eval(string_array)
    except (ValueError, SyntaxError):
        print("Invalid array string.")
        actual_array = []

    return actual_array


def checkIfContainsWord(word, target_word):
    """
    Check if the word contains the target word, regardless of case. In this
    instance contains refers to a whole word, and not substrings of a word. For
    example if you are looking for the word char

    char-grilled salmon would return true
    charcuterie would return false

    :param word: word you are checking
    :param target_word: word you are looking for
    :return: true if the word contains the target word, false otherwise
    """

    # Regex to find the word
    pattern = r'\b' + re.escape(target_word) + r'\b'
    match = re.search(pattern, word.lower())

    return match


def getScoreForCookingMethod(recipe_name, score_dict, method_to_rec):
    """
    Given a recipe name, a dictionary that contains the scores for each
    recipe, and a dictionary that contains the recommendation for each
    method, return the score for the recipe. We check if the recipe name
    contains the cooking method and then adjust the score from there

    :param recipe_name: name of the recipe

    :param score_dict: dictionary that contains the score for each recommendation.
    the KVP is <reccomendation, score>

    :param method_to_rec: dictionary that contains the recommendation for
    each method. The KVP is <method_name, Reccomendation>

    :return: the score for the recipe
    """

    current_score = 0

    for method, rec in method_to_rec.items():
        if checkIfContainsWord(recipe_name, method):
            current_score += score_dict[rec]

    return current_score


def updateMealDBWithDietScore(meal_csv_name, method_csv_name, ingred_csv_name,
                              column_name):
    """
    Given a meal, method and an ingredient csv, update the meal csv with a
    diet score based off of the methods and ingredients, using the methodology
    outlined at the top of the file

    :param meal_db_csv: csv file for the meal database
    :param method_csv: csv file for the method and recommendation
    :param ingred_csv: csv file for the ingredient and recommendation
    :param column_name: name for the diet_score column
    """
    PREF_SCORE = 2
    LIMIT_SCORE = -1
    NEUTRAL_SCORE = 1

    SCORE_DICT = {"preferred": PREF_SCORE,
                  "limit": LIMIT_SCORE,
                  "neutral": NEUTRAL_SCORE}

    diet_score = []

    meal_db_df = pd.read_csv(meal_csv_name)
    ingred_df = pd.read_csv(ingred_csv_name)
    method_df = pd.read_csv(method_csv_name)

    # dictionary that contains the recomendation for an ingredient
    ingred_to_rec = dict(zip(ingred_df["ingredient"],
                             ingred_df["recommendation"]))

    # dictionary that contains the recomendation for a cooking method
    method_to_rec = dict(zip(method_df["method"],
                             method_df["recommendation"]))

    for index in range(len(meal_db_df)):
        current_score = 0
        title = meal_db_df["title"][index]
        ingredient_array_str = meal_db_df["ingredients"][index]

        # arrays in the csv are stored as string so need to convert them
        ingredient_list = convertStringToArray(ingredient_array_str)

        for ingredient in ingredient_list:
            if ingredient in ingred_to_rec:
                if ingred_to_rec[ingredient] == "exclude":
                    current_score = 0
                    break
                current_score += SCORE_DICT[ingred_to_rec[ingredient]]

        current_score += getScoreForCookingMethod(title, SCORE_DICT,
                                                  method_to_rec)
        diet_score.append(current_score)

    meal_db_df[column_name] = diet_score
    meal_db_df.to_csv(meal_csv_name, index=False)


def main():
    # driver for testing the file
    updateMealDBWithDietScore(meal_csv_name="meal_database.csv",
                              method_csv_name="fight_cancer_methods.csv",
                              ingred_csv_name="fight_cancer_ingreds.csv",
                              column_name="fight_cancer_score")

if __name__ == "__main__":
    main()
