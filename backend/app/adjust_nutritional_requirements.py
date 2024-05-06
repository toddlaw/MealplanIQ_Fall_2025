def adjust_nutrients(macros, micros, health_plan, people):
    """
    Called in ./backend/app/generate_meal_plan.py.
    Adjusts the nutritional requirements based on the health plan.
    :param macros: dict of macronutrient requirements
    :param micros: dict of micronutrient requirements
    :param health_plan: string of health plan
    :param people: list of people objects
    """
    if health_plan == 'fight_cancer':
        adjust_for_fight_cancer(macros, people)
    elif health_plan == 'fight_diabetes':
        adjust_for_fight_diabetes(macros, micros, people)
    elif health_plan == 'fight_heart_disease':
        adjust_for_fight_heart_disease(micros, people)
    elif health_plan == 'sports_build_muscle':
        adjust_for_sports_build_muscle(macros, micros, people)
    elif health_plan == 'lose_weight':
        adjust_for_lose_weight(macros, people)
    

def adjust_for_fight_cancer(macros, people):
    """
    Called in ./backend/app/adjust_nutritional_requirements.py.
    Adjusts the nutritional requirements for the fight cancer health plan.
    :param macros: dict of macronutrient requirements
    :param people: list of people objects
    """
    large_calories = macros['large_calories']
    macros['carbohydrates_g'][0] = large_calories * 0.5 / 4
    macros['carbohydrates_g'][1] = large_calories * 0.6 / 4
    macros['fat_g'][0] = large_calories * 0.2 / 9
    macros['fat_g'][1] = large_calories * 0.3 / 9
    macros['fiber_g'][0] = 25 * len(people)
    macros['fiber_g'][1] = 30 * len(people)
    macros['protein_g'][0] = 1.1 * sum([person['weight'] for person in people])
    macros['protein_g'][1] = 1.45 * sum([person['weight'] for person in people])

def adjust_for_fight_diabetes(macros, micros, people):
    """
    Called in ./backend/app/adjust_nutritional_requirements.py.
    Adjusts the nutritional requirements for the fight diabetes health plan.
    :param macros: dict of macronutrient requirements
    :param micros: dict of micronutrient requirements
    :param people: list of people objects
    """
    large_calories = macros['large_calories']
    macros['carbohydrates_g'][0] = large_calories * 0.45 / 4
    macros['carbohydrates_g'][1] = large_calories * 0.6 / 4
    macros['fat_g'][0] = large_calories * 0.2 / 9
    macros['fat_g'][1] = large_calories * 0.35 / 9
    macros['fiber_g'][0] = 25 * len(people)
    macros['fiber_g'][1] = 38 * len(people)
    macros['protein_g'][0] = large_calories * 0.1 / 4
    macros['protein_g'][1] = large_calories * 0.2 / 4
    micros['min_sodium_mg_ai'] = 1500 * len(people)
    micros['min_sodium_mg_ul'] = 2300 * len(people)

def adjust_for_fight_heart_disease(micros, people):
    """
    Called in ./backend/app/adjust_nutritional_requirements.py.
    Adjusts the nutritional requirements for the fight heart disease health plan.
    :param micros: dict of micronutrient requirements
    :param people: list of people objects
    """
    sodium_mg_ai = micros['min_sodium_mg_ai']
    sodium_mg_ul = micros['min_sodium_mg_ul']
    difference = sodium_mg_ul - sodium_mg_ai
    range_value = 300 * len(people)

    # Lower the sodium upper limit if the difference of the sodium upper limit and sodium adequate intake is 
    # greater than the range value which is between the upper limit and adequate intake (300 mg * number of people)
    if difference > range_value:
        micros['min_sodium_mg_ul'] = sodium_mg_ul - (difference - range_value)

def adjust_for_sports_build_muscle(macros, micros, people):
    """
    Called in ./backend/app/adjust_nutritional_requirements.py.
    Adjusts the nutritional requirements for the sports build muscle health plan.
    :param macros: dict of macronutrient requirements
    :param micros: dict of micronutrient requirements
    :param people: list of people objects
    """
    large_calories = macros['large_calories']
    macros['protein_g'][0] = 1.6 * sum([person['weight'] for person in people])
    macros['protein_g'][1] = 2.2 * sum([person['weight'] for person in people])
    macros['fat_g'][0] = large_calories * 0.2 / 9
    macros['fat_g'][1] = large_calories * 0.35 / 9
    macros['fiber_g'][0] = 25 * len(people)
    macros['fiber_g'][1] = 38 * len(people)
    micros['min_iron_mg_rda'] = (micros['min_iron_mg_rda'] + micros['min_iron_mg_ul']) / 2
    micros['vit_d_iu_ai'] = (micros['vit_d_iu_ai']) + (0.25 * (micros['vit_d_iu_ul'] - micros['vit_d_iu_ai']))

def adjust_for_lose_weight(macros, people):
    macros['large_calories'] -= 500 * len(people)