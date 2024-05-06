# As per https://www150.statcan.gc.ca/n1/pub/82-003-x/2008004/article/10703/t/5800493-eng.htm#:~:text=EER%20%3D%20%2D114.1%2D50.9*,and%201.45%20if%20very%20active

@staticmethod
def energy_calculator_function(age, bmi, gender, weight, height, activity_level):
    """
    original energy calculator
    :param age: int, age in years
    :param bmi: float
    :param gender: string, first letter must be capitalized
    :param weight: int in kg
    :param height: int in cm
    :param activity_level: String, Sedentary, Low_Active, Active, or Very_Active
    :return: total daily energy intake
    """
    height_m = height / 100.0
    if 18.5 < bmi <= 25 and 9 <= age <= 18 and gender == 'Male':
        if activity_level == 'Sedentary':
            pal = 1.0
        elif activity_level == 'Low_Active':
            pal = 1.13
        elif activity_level == 'Active':
            pal = 1.26
        elif activity_level == 'Very_Active':
            pal = 1.42
        result = 113.5 - 61.9 * age + pal * (26.7 * weight + 903 * height_m)
    elif 18.5 < bmi <= 25 and 9 <= age <= 18 and gender == 'Female':
        if activity_level == 'Sedentary':
            pal = 1.0
        elif activity_level == 'Low_Active':
            pal = 1.16
        elif activity_level == 'Active':
            pal = 1.31
        elif activity_level == 'Very_Active':
            pal = 1.56
        result = 160.3 - 30.8 * age + pal * (10 * weight + 934 * height_m)
    elif 18.5 < bmi <= 25 and age >= 19 and gender == 'Male':
        if activity_level == 'Sedentary':
            pal = 1.0
        elif activity_level == 'Low_Active':
            pal = 1.11
        elif activity_level == 'Active':
            pal = 1.25
        elif activity_level == 'Very_Active':
            pal = 1.48
        result = 661.8 - 9.53 * age + pal * (15.91 * weight + 539.6 * height_m)
    elif 18.5 < bmi <= 25 and age >= 19 and gender == 'Female':
        if activity_level == 'Sedentary':
            pal = 1.0
        elif activity_level == 'Low_Active':
            pal = 1.12
        elif activity_level == 'Active':
            pal = 1.27
        elif activity_level == 'Very_Active':
            pal = 1.45
        result = 354.1 - 6.91 * age + pal * (9.36 * weight + 726 * height_m)
    elif bmi > 25 and 9 <= age <= 18 and gender == 'Male':
        if activity_level == 'Sedentary':
            pal = 1.0
        elif activity_level == 'Low_Active':
            pal = 1.12
        elif activity_level == 'Active':
            pal = 1.24
        elif activity_level == 'Very_Active':
            pal = 1.45
        result = -114.1 - 50.9 * age + pal * (19.5 * weight + 1161.4 * height_m)
    elif bmi > 25 and 9 <= age <= 18 and gender == 'Female':
        if activity_level == 'Sedentary':
            pal = 1.0
        elif activity_level == 'Low_Active':
            pal = 1.18
        elif activity_level == 'Active':
            pal = 1.35
        elif activity_level == 'Very_Active':
            pal = 1.60
        result = 389.2 - 41.2 * age + pal * (15 * weight + 701.6 * height_m)
    elif bmi > 25 and age >= 19 and gender == 'Male':
        if activity_level == 'Sedentary':
            pal = 1.0
        elif activity_level == 'Low_Active':
            pal = 1.12
        elif activity_level == 'Active':
            pal = 1.29
        elif activity_level == 'Very_Active':
            pal = 1.59
        result = 1085.6 - 10.08 * age + pal * (13.7 * weight + 416 * height_m)
    elif bmi > 25 and age >= 19 and gender == 'Female':
        if activity_level == 'Sedentary':
            pal = 1.0
        elif activity_level == 'Low_Active':
            pal = 1.16
        elif activity_level == 'Active':
            pal = 1.27
        elif activity_level == 'Very_Active':
            pal = 1.44
        result = 447.6 - 7.95 * age + pal * (11.4 * weight + 619 * height_m)

    return result
