import datetime
import json


def extract_user_profile_data_from_json(data, user_id):
    person = data.get('people')[0] if data.get('people') else {}
    return {
        'user_id': user_id,
        'gender': person.get('gender'),
        'height': person.get('height'),
        'weight': person.get('weight'),
        'age': person.get('age'),
        'activity_level': person.get('activityLevel'),
        'selected_unit': data.get('selectedUnit'),
        'health_goal': data.get('healthGoal')
    }


def extract_data_from_json(data):
    return {
        # 'maxDate': data.get('maxDate'),
        'allergies': data.get('allergies'),
        'liked_foods': data.get('likedFoods'),
        'disliked_foods': data.get('dislikedFoods'),
        'favourite_cuisines': data.get('favouriteCuisines'),
        'religious_constraint': data.get('religiousConstraint'),
        'dietary_constraint': data.get('dietaryConstraint'),
        'snacks': data.get('snacks'),
        'breakfasts': data.get('breakfasts')
    }


def process_user_data(db, user_id, extract_data):
    # db.update_user_last_date_plan_profile(user_id, extract_data['maxDate'])
    db.update_user_allergies(user_id, extract_data['allergies'])
    db.update_user_liked_foods(user_id, extract_data['liked_foods'])
    db.update_user_disliked_foods(user_id, extract_data['disliked_foods'])
    db.update_user_favourite_cuisines(
        user_id, extract_data['favourite_cuisines'])
    db.insert_or_update_user_religious_constraint(
        user_id, extract_data['religious_constraint'])
    db.insert_or_update_user_dietary_constraint(
        user_id, extract_data['dietary_constraint'])
    db.update_user_prefered_snacks(user_id, extract_data['snacks'])
    db.update_user_prefered_breakfasts(user_id, extract_data['breakfasts'])

# Return the dictionary that is used as input for gen_meal_plan for email scheduler
def create_data_input_for_auto_gen_meal_plan(db, user_id, start_date, end_date):
    dietary_constraints = db.retrieve_user_dieatary_constraints(user_id)
    if not dietary_constraints:
        dietary_constraint = None
    else:
        dietary_constraint = dietary_constraints[0].lower()
    profile_json = db.retrieve_user_profile_json(user_id)
    if isinstance(profile_json, str):
        profile_data = json.loads(profile_json)
    else:
        profile_data = profile_json

    people = [profile_data]
    selected_unit = db.retrieve_user_selected_unit(user_id)
    dietary_constraint = db.retrieve_user_dieatary_constraints(user_id) or "none"
    health_goal = db.retrieve_user_health_goal(user_id)
    religious_constraint = db.retrieve_user_religious_constraints(user_id) or "none"
    liked_foods = db.retrieve_user_liked_food(user_id)
    disliked_foods = db.retrieve_user_disliked_food(user_id)
    favourite_cuisines = db.retrieve_user_favourite_cuisines(user_id)
    allergies = db.retrieve_user_allergies(user_id)
    snacks = db.retrieve_user_snack_preferences(user_id)
    breakfasts = db.retrieve_user_breakfast_preferences(user_id)
    min_date = int(start_date.timestamp() * 1000)
    max_date = int(end_date.timestamp() * 1000)
    included_recipes = []
    excluded_recipes = []
    return {
        'people': people,
        'selectedUnit': selected_unit,
        'user_id': user_id,
        'dietaryConstraint': dietary_constraint,
        'healthGoal': health_goal,
        'religiousConstraint': religious_constraint,
        'likedFoods': liked_foods,
        'dislikedFoods': disliked_foods,
        'favouriteCuisines': favourite_cuisines,
        'allergies': allergies,
        'minDate': min_date,
        'maxDate': max_date,
        'snacks': snacks,
        'breakfasts': breakfasts,
        'includedRecipes': included_recipes,
        'excludedRecipes': excluded_recipes
    }


def _get_min_and_max_date_from_the_last_date(db, user_id):
    last_meal_plan_date_in_milliseconds = db.retrieve_user_last_date_plan_profile(
        user_id)
    timestamp_seconds = last_meal_plan_date_in_milliseconds / 1000.0
    base_date = datetime.datetime.fromtimestamp(
        timestamp_seconds, datetime.timezone.utc)
    min_date_time_datetime_obj = base_date + datetime.timedelta(days=1)
    min_date = int(min_date_time_datetime_obj.timestamp() * 1000)
    max_date_time_datetime_obj = base_date + datetime.timedelta(days=7)
    max_date = int(max_date_time_datetime_obj.timestamp() * 1000)
    return min_date, max_date
