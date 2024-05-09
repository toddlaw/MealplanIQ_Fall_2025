
def bmi_calculator_function(weight, height):
    """
    original bmi calculator
    :param weight: weight in kgs
    :param height: height in cm
    :return: bmi
    """
    height_m = height / 100.0
    bmi = weight / (height_m * height_m)

    return bmi
