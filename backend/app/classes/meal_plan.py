from app.calculate_bmi import bmi_calculator_function
from app.calculate_energy import energy_calculator_function
from app.calculate_nutritional_requirements import (
    calculate_macros,
    calculate_micros,
    distribute_nutrients,
)
from app.adjust_nutritional_requirements import adjust_nutrients
from app.retrieve_diet import get_diet_plan
import datetime
import pandas as pd
from app.apply_user_prefs_to_meal_database import apply_user_prefs


class MealPlan:
    """
    A class to represent and process a meal plan.
    """

    def __init__(self, data):
        """
        Initializes the MealPlan with data from the frontend.
        """

        self.data = data
        # data is the dictionary data this meal plan organized and will be pass to the client after process

        # process calculations
        self.__calculate_bmi()
        self.__calculate_energy()
        self.__get_distributed_micro_and_macro_nutrients()

        self.__generate_recipes_in_categories()

    def __calculate_bmi(self):
        """
        Calculates the BMI for each person and stores it in the bmi attribute.

        The method processes each person's weight and height, converts units if necessary,
        and calculates their BMI using the bmi_calculator_function. The calculated BMI
        values are stored in the bmi attribute.
        """
        # Calculate BMI and stored it in the array according to the people's data
        bmi = []

        # convert heights and weights if necessary
        for person in self.data["people"]:
            if self.data["selectedUnit"] == "imperial":
                person["weight"] = person["weight"] * 0.453592
                person["height"] = person["height"] * 2.54
            bmi.append(bmi_calculator_function(person["weight"], person["height"]))

        self.__bmi = bmi

    def __calculate_energy(self):
        """
        Calculates the energy requirements for each person and stores it in the energy attribute.
        """
        energy = []

        for i, person in enumerate(self.data["people"]):
            energy.append(
                energy_calculator_function(
                    person["age"],
                    self.__bmi[i],
                    person["gender"],
                    person["weight"],
                    person["height"],
                    person["activityLevel"],
                )
            )
        self.__energy = energy

    def __get_distributed_micro_and_macro_nutrients(self):
        """
        Distributes the daily micro and macro nutrients after health goal adjustments to breakfast, snack, and main meal in the meal plan.

        :return: dict, containing nutrient requirements distributed into breakfast, snacks, and meals
        """

        macros = calculate_macros(self.__energy, self.data["people"])

        micros = calculate_micros(self.data["people"])

        # etrieve diet
        diet_info = get_diet_plan(self.data["healthGoal"])

        adjust_nutrients(macros, micros, diet_info["plan"], self.data["people"])

        self.__distributed__micro_and_macro_nutritions = distribute_nutrients(
            macros, micros
        )

    def __generate_recipes_in_categories(self):
        """
        Generates recipes for each meal category in the meal plan.
        """

        self.__mainmeal_recipes_with_scores = apply_user_prefs(
            self.data["favouriteCuisines"],
            self.data["dietaryConstraint"],
            self.data["religiousConstraint"],
            self.data["likedFoods"],
            self.data["dislikedFoods"],
            self.data["allergies"],
            pd.read_csv("./meal_db/meal_database.csv"),
        )

        # replace these 2 with real database, need to modify the preference data
        self.__breakfast_recipes_with_scores = self.__mainmeal_recipes_with_scores

        self.__snack_recipes_with_scores = self.__mainmeal_recipes_with_scores

    def __calculate_days(self):
        """
        Calculates the number of days for the meal plan.
        """
        min_date = datetime.datetime.fromtimestamp(
            self.data["minDate"] / 1000.0, datetime.timezone.utc
        )
        max_date = datetime.datetime.fromtimestamp(
            self.data["maxDate"] / 1000.0, datetime.timezone.utc
        )
        # Calculating the difference in days
        difference = max_date - min_date
        self.__days = difference.days + 1


def main():
    df = pd.read_csv("./meal_db/new_meal_database.csv")

    snack_data = df[df["meal_slot"] == "['snack']"]
    print(snack_data.head(5))


if __name__ == "__main__":
    main()
