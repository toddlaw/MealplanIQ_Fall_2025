import pandas as pd

def calculate_macros(large_calories, people):
    """
    Called in ./backend/app/generate_meal_plan.py.
    Calculates the daily macronutrient requirements for a group of people.
    :param large_calories: numeric list of large calories for each person
    :param people: list of people
    :return: dict of macronutrient requirements 
    """
    total_range_carbohydrates = [0, 0]
    total_range_fat = [0, 0]
    total_range_fiber = [0, 0]
    total_range_protein = [0, 0]

    for i, person in enumerate(people):
        carbohydrates = [large_calories[i] * 0.45 / 4, large_calories[i] * 0.65 / 4]
        # Max Int value in Java as the fiber upper bound
        fiber = [large_calories[i] / 1000 * 14, (2 ** 31) - 1]
        protein_lower = large_calories[i] / 40
        protein = [protein_lower, protein_lower * 3.5]

        if person['age'] <= 3:
            fat = [large_calories[i] * 0.3 / 9, large_calories[i] * 0.4 / 9]
        elif 4 <= person['age'] <= 18:
            fat = [large_calories[i] * 0.25 / 9, large_calories[i] * 0.35 / 9]
        else:
            fat = [large_calories[i] * 0.2 / 9, large_calories[i] * 0.35 / 9]

        # Sum up the macronutrients for each person with the total
        for j in range(2):
            total_range_carbohydrates[j] += carbohydrates[j]
            total_range_fiber[j] += fiber[j]
            total_range_fat[j] += fat[j]
            total_range_protein[j] += protein[j]

    macros = {
        "carbohydrates_g": total_range_carbohydrates,
        "fat_g": total_range_fat,
        "fiber_g": total_range_fiber,
        "protein_g": total_range_protein,
        "large_calories": sum(large_calories)
    }

    return macros

def calculate_micros(people):
    """
    Called in ./backend/app/generate_meal_plan.py.
    Calculates the daily micronutrient requirements for a group of people using the DietUSDA.xlsx file.
    :param people: list of people objects
    :return: dict of summed up micronutrient requirements
    """
    micros_info = read_micro_nutrients_file()
    micros_people = []
    micros = {}

    for person in people:
        age_days = person['age'] * 365
        micros_person = {}

        # Get row index in the DietUSDA.xlsx file
        # Skip the first two rows as they are for infants
        for i in range(2, 15):
            if micros_info['age_days_lower'][i] <= age_days <= micros_info['age_days_upper'][i] and person['gender'].lower() == micros_info['gender'][i]:
                row_index = i
                break

        # Exclude the non micro-nutrient keys
        micros_keys = list(micros_info.keys())[3:]

        for i, key in enumerate(micros_keys):
            micros_person[key] = micros_info[key][row_index]

        micros_people.append(micros_person)

    max_int = (2 ** 31) - 1 # Max int value in Java

    # Sum up the micronutrients for each person
    for key in micros_keys:
        # If a key value is ND, make it the max int value in Java
        if micros_people[0][key] == 'ND':
            micros[key] = max_int
        else:
            micros[key] = sum(float(micros_person[key]) for micros_person in micros_people)

    return micros

def read_micro_nutrients_file():
    """
    Called in ./backend/app/calculate_nutritional_requirements.py.
    Reads the DietUSDA.xlsx file to get the recommended micro nutrient requirements.
    :return: dict of micro nutrient requirements
    """
    # No foline or carotene in DietUSDA.xlsx
    columns = ['gender', 'age_days_lower', 'age_days_upper', 'min_calcium_mg_ai', 'min_calcium_mg_ul', 
               'min_phosphorus_mg_rda', 'min_phosphorus_g_ul', 'min_potassium_mg_ai', 'min_potassium_ul',
               'min_magnesium_mg_rda', 'min_magnesium_mg_ul', 'min_sodium_mg_ai', 'min_sodium_mg_ul', 'min_iron_mg_rda', 
               'min_iron_mg_ul', 'min_copper_mg_rda', 'min_copper_mg_ul', 'min_zinc_mg_rda', 'min_zinc_mg_ul', 
               'min_manganese_mg_rda', 'min_manganese_mg_ul', 'min_selenium_ug_rda', 'min_selenium_ug_ul', 'min_fluoride_mg_ai', 
               'min_fluoride_mg_ul', 'vit_a_iu_rda', 'vit_a_iu_ul', 'vit_b1_thiamin_mg_rda', 'vit_b1_thiamin_mg_ul', 
               'vit_b2_riboflavin_mg_rda', 'vit_b2_riboflavin_mg_ul', 'vit_b3_niacin_mg_rda', 'vit_b3_niacin_mg_ul',
               'vit_b5_pantothenicacid_mg_ai', 'vit_b5_pantothenic_acid_mg_ul', 'vit_b6_mg_rda', 'vit_b6_mg_ul', 'vit_b12_ug_rda', 
               'vit_b12_ug_ul', 'vit_b9_folate_ug_rda', 'vit_b9_folate_ug_ul', 'vit_c_mg_rda', 'vit_c_mg_ul', 'vit_d_iu_ai', 
               'vit_d_iu_ul', 'vit_e_mg_rda', 'vit_e_mg_ul', 'vit_k_ug_ai', 'vit_k_ug_ul', 'vit_choline_mg_ai', 'vit_choline_mg_ul'
            ]
    
    # Only 16 rows because we don't need pregnant or lactating rows
    return pd.read_csv('./nutri_requirements/DietUSDA.csv', usecols = columns, nrows = 16).to_dict()


#2024 NEW FUNCTION
def distribute_nutrients(macros, micros):
    """
    Distributes macronutrient and micronutrient requirements into breakfast, snacks, and main meals.

    :param macros: dict, containing macronutrient requirements
    :param micros: dict, containing micronutrient requirements
    :return: dict, containing nutrient requirements distributed into breakfast, snacks, and meals
    """
    distribution_ratios = {
        "breakfast": 0.2,
        "snacks": 0.1,
        "meals": 0.7
    }

    distributed_macros = {
        "breakfast": {},
        "snacks": {},
        "meals": {}
    }

    distributed_micros = {
        "breakfast": {},
        "snacks": {},
        "meals": {}
    }

    # Distribute macronutrients
    for key, value in macros.items():
        if isinstance(value, list):  # If the value is a range (list)
            distributed_macros["breakfast"][key] = [v * distribution_ratios["breakfast"] for v in value]
            distributed_macros["snacks"][key] = [v * distribution_ratios["snacks"] for v in value]
            distributed_macros["meals"][key] = [v * distribution_ratios["meals"] for v in value]
        else:  # If the value is a single number (e.g., total calories)
            distributed_macros["breakfast"][key] = value * distribution_ratios["breakfast"]
            distributed_macros["snacks"][key] = value * distribution_ratios["snacks"]
            distributed_macros["meals"][key] = value * distribution_ratios["meals"]

    # Distribute micronutrients
    for key, value in micros.items():
        distributed_micros["breakfast"][key] = value * distribution_ratios["breakfast"]
        distributed_micros["snacks"][key] = value * distribution_ratios["snacks"]
        distributed_micros["meals"][key] = value * distribution_ratios["meals"]

    distributed_nutrients = {
        "macros": distributed_macros,
        "micros": distributed_micros
    }

    return distributed_nutrients
