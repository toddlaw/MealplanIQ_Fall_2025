import datetime
import os
import pymysql
from dotenv import load_dotenv
import json

from .initiate_db import DatabaseSchemaManager

load_dotenv()


class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if not self.initialized:
            self.db = self.connect_to_database()
            self.initialized = True
            schema_manager = DatabaseSchemaManager(self.db)
            schema_manager.create_all_tables()
            schema_manager.populate_dictionary_tables()

    @staticmethod
    def connect_to_database():
        print("begin to instantiate database -------------")
        print("DB_HOST:", os.getenv('DB_HOST'))
        print("DB_USER:", os.getenv('DB_USER'))
        print("DB_PASSWORD:", os.getenv('DB_PASSWORD'))
        print("DB_NAME:", os.getenv('DB_NAME'))
        
        try:
            connection = pymysql.connect(
                # unix_socket=os.getenv('DB_HOST'), 
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME'),
                charset='utf8'
            )
            print("Database connection established successfully!")
            return connection
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def disconnect_from_database(self):
        self.db.close()

    

    # ------------------- Insert data with inputs -------------------

    def insert_user_and_set_default_subscription_signup(self, user_id, user_name, email, last_meal_plan_date=None, gender=None, height=None, age=None, weight=None, activity_level=None, selected_unit=None, health_goal=None):
        cursor = self.db.cursor()

        # Insert into user_profile
        sql_user_profile = """
        INSERT INTO user_profile (user_id, user_name, email, gender, last_meal_plan_date, height, age, weight, activity_level, selected_unit, health_goal)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        values_user_profile = (user_id, user_name, email, gender, last_meal_plan_date,
                               height, age, weight, activity_level, selected_unit, health_goal)
        sql_subscription = """
        INSERT INTO user_subscription (user_id, subscription_type_id, stripe_customer_id, subscription_stripe_id, subscription_expiry_date)
        VALUES (%s, 1, NULL, NULL, NULL);
        """
        values_subscription = (user_id,)  # Subscription values for the user

        try:
            cursor.execute(sql_user_profile, values_user_profile)
            cursor.execute(sql_subscription, values_subscription)
            self.db.commit()
            return {"success": True, "message": "User profile and subscription created successfully."}
        except pymysql.Error as e:
            self.db.rollback()
            return {"success": False, "msg": f"Error inserting user profile and subscription for user_id {user_id}: {str(e)}"}
        
    def _insert_additional_user_info(self, user_id: str, user_data: dict):
        if allergies := user_data.get("allergies"):
            self.update_user_allergies(user_id, allergies)
        if liked_food := user_data.get("likedFoods"):
            self.update_user_liked_foods(user_id, liked_food)
        if disliked_food := user_data.get("dislikedFoods"):
            self.update_user_disliked_foods(user_id, disliked_food)
        if cuisines := user_data.get("favouriteCuisines"):
            self.update_user_favourite_cuisines(user_id, cuisines)
        if dc := user_data.get("dietaryConstraint"):
            self.insert_or_update_user_dietary_constraint(user_id, dc)
        if rc := user_data.get("religiousConstraint"):
            self.insert_or_update_user_religious_constraint(user_id, rc)
        if snacks := user_data.get("snacks"):
            self.update_user_prefered_snacks(user_id, snacks)
        if breakfasts := user_data.get("breakfasts"):
            self.update_user_prefered_breakfasts(user_id, breakfasts)
            
    def insert_new_user_with_paid_trial(self, user_data: dict):
        cursor = self.db.cursor()

        sql_user_profile = """
        INSERT INTO user_profile (user_id, user_name, email, gender, last_meal_plan_date, height, age, weight, activity_level, selected_unit, health_goal)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        values_user_profile = (
            user_data.get("user_id"),
            user_data.get("user_name"),
            user_data.get("email"),
            user_data.get("gender"),
            None,  # last_meal_plan_date
            user_data.get("height"),
            user_data.get("age"),
            user_data.get("weight"),
            user_data.get("activity_level"),
            user_data.get("selected_unit"),
            user_data.get("health_goal")
        )

        sql_subscription = """
        INSERT INTO user_subscription (user_id, subscription_type_id, subscription_stripe_id, stripe_customer_id, subscription_expiry_date)
        VALUES (%s, %s, %s, %s, %s);
        """
        values_subscription = (
            user_data.get("user_id"),
            2, # paid trial subscription status
            user_data.get("subscription_id"),
            user_data.get("customer_id"),
            user_data.get("trial_end")
        )

        try:
            cursor.execute(sql_user_profile, values_user_profile)
            cursor.execute(sql_subscription, values_subscription)
            self._insert_additional_user_info(user_data.get("user_id"), user_data)
            self.db.commit()
            return {"success": True, "message": "User profile and paid subscription created successfully."}
        except pymysql.Error as e:
            self.db.rollback()
            return {"success": False, "msg": f"DB Error: {str(e)}"}


    # def insert_user_profile(self, user_id, user_name, email, gender=None, height=None, age=None, weight=None, activity_level=None, selected_unit=None, health_goal=None):
    #     cursor = self.db.cursor()
    #     sql = """
    #     INSERT INTO user_profile (user_id, user_name, email, gender, height, age, weight, activity_level, selected_unit, health_goal)
    #     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    #     """
    #     values = (user_id, user_name, email, gender, height, age, weight, activity_level, selected_unit, health_goal)
    #     try:
    #         cursor.execute(sql, values)
    #         self.db.commit()
    #         print("User profile inserted successfully.")
    #     except pymysql.Error as e:
    #         self.db.rollback()
    #         print(f"Error inserting user profile: {e}")

    # def insert_default_subscription(self, user_id):
    #     cursor = self.db.cursor()
    #     # Assuming '3' is the subscription_type_id for 'free_trial' as per your populate_table_sql
    #     sql = """
    #     INSERT INTO user_subscription (user_id, subscription_type_id, subscription_stripe_id, subscription_expiry_date)
    #     VALUES (%s, 3, NULL, NULL);
    #     """
    #     try:
    #         cursor.execute(sql, (user_id,))
    #         self.db.commit()
    #         print("Default free trial subscription added successfully for user_id:", user_id)
    #     except pymysql.Error as e:
    #         self.db.rollback()
    #         print(f"Error inserting default subscription for user_id {user_id}: {e}")

    def update_user_profile(self, user_id, gender, height, age, weight, activity_level, selected_unit, health_goal):
        cursor = self.db.cursor()
        sql = """
        UPDATE user_profile
        SET gender = %s, height = %s, age = %s, weight = %s, activity_level = %s, selected_unit = %s, health_goal = %s
        WHERE user_id = %s;
        """
        values = (gender, height, age, weight, activity_level,
                  selected_unit, health_goal, user_id)
        try:
            cursor.execute(sql, values)
            self.db.commit()
            print("USER PROFILE updated successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error updating user profile: {e}")

    def update_user_profile_from_dashboard(self, user_name, email, age,  gender, height, weight, activity_level, health_goal, selected_unit, user_id):
        cursor = self.db.cursor()
        sql = """
        UPDATE user_profile
        SET user_name = %s, gender = %s, height = %s, age = %s, weight = %s, activity_level = %s, email = %s, health_goal = %s, selected_unit = %s
        WHERE user_id = %s;
        """
        values = (user_name, gender, height, age,
                  weight, activity_level, email, health_goal, selected_unit, user_id)
        try:
            cursor.execute(sql, values)
            self.db.commit()
            print("USER PROFILE updated successfully from dashboard.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error updating user profile from dashboard: {e}")

    def insert_or_update_user_dietary_constraint(self, user_id, dietary_constraint_name):
        cursor = self.db.cursor()
        find_constraint_id_sql = """
        SELECT id FROM dietary_constraints WHERE name = %s;
        """
        check_existing_sql = """
        SELECT dietary_constraint_id FROM user_dietary_constraints WHERE user_id = %s;
        """
        update_sql = """
        UPDATE user_dietary_constraints SET dietary_constraint_id = %s WHERE user_id = %s;
        """
        insert_sql = """
        INSERT INTO user_dietary_constraints (user_id, dietary_constraint_id)
        VALUES (%s, %s);
        """
        try:
            cursor.execute(find_constraint_id_sql, (dietary_constraint_name,))
            result = cursor.fetchone()
            if result:
                dietary_constraint_id = result[0]
                cursor.execute(check_existing_sql, (user_id,))
                existing_constraint = cursor.fetchone()

                if existing_constraint:
                    cursor.execute(
                        update_sql, (dietary_constraint_id, user_id))
                    print("User dietary constraint updated successfully.")
                else:
                    cursor.execute(
                        insert_sql, (user_id, dietary_constraint_id))
                    print("User dietary constraint inserted successfully.")

                self.db.commit()
            else:
                print("No dietary constraint found with that name.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error in database operation: {e}")

    def insert_or_update_user_religious_constraint(self, user_id, religious_constraint_name):
        cursor = self.db.cursor()
        find_constraint_id_sql = """
        SELECT id FROM religious_constraints WHERE name = %s;
        """
        check_existing_sql = """
        SELECT religious_constraint_id FROM user_religious_constraints WHERE user_id = %s;
        """
        update_sql = """
        UPDATE user_religious_constraints SET religious_constraint_id = %s WHERE user_id = %s;
        """
        insert_sql = """
        INSERT INTO user_religious_constraints (user_id, religious_constraint_id)
        VALUES (%s, %s);
        """
        try:
            cursor.execute(find_constraint_id_sql,
                           (religious_constraint_name,))
            result = cursor.fetchone()
            if result:
                religious_constraint_id = result[0]
                cursor.execute(check_existing_sql, (user_id,))
                existing_constraint = cursor.fetchone()

                if existing_constraint:
                    cursor.execute(
                        update_sql, (religious_constraint_id, user_id))
                    print("User religious constraint updated successfully.")
                else:
                    cursor.execute(
                        insert_sql, (user_id, religious_constraint_id))
                    print("User religious constraint inserted successfully.")

                self.db.commit()
            else:
                print("No religious constraint found with that name.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error in database operation: {e}")

    def insert_user_allergies(self, user_id, allergy_name):
        cursor = self.db.cursor()
        find_id_sql = """
        SELECT id FROM allergies WHERE name = %s;
        """
        insert_sql = """
        INSERT INTO user_allergies (user_id, allergy_id)
        VALUES (%s, %s);
        """
        try:
            cursor.execute(find_id_sql, (allergy_name,))
            result = cursor.fetchone()
            if result:
                allergy_id = result[0]
                cursor.execute(insert_sql, (user_id, allergy_id))
                self.db.commit()
                print("User allergy inserted successfully.")
            else:
                print("No allergy found with that name.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error inserting user allergy: {e}")

    def insert_user_favourite_cuisines(self, user_id, cuisine_name):
        cursor = self.db.cursor()
        find_id_sql = """
        SELECT id FROM favourite_cuisines WHERE name = %s;
        """
        insert_sql = """
        INSERT INTO user_favourite_cuisines (user_id, cuisine_id)
        VALUES (%s, %s);
        """
        try:
            cursor.execute(find_id_sql, (cuisine_name,))
            result = cursor.fetchone()
            if result:
                cuisine_id = result[0]
                cursor.execute(insert_sql, (user_id, cuisine_id))
                self.db.commit()
                print("User favourite cuisine inserted successfully.")
            else:
                print("No cuisine found with that name.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error inserting user favourite cuisine: {e}")

    def insert_user_liked_food(self, user_id, food_name):
        cursor = self.db.cursor()
        find_id_sql = """
        SELECT id FROM liked_food WHERE name = %s;
        """
        insert_sql = """
        INSERT INTO user_liked_food (user_id, liked_food_id)
        VALUES (%s, %s);
        """
        try:
            cursor.execute(find_id_sql, (food_name,))
            result = cursor.fetchone()
            if result:
                food_id = result[0]
                cursor.execute(insert_sql, (user_id, food_id))
                self.db.commit()
                print("User liked food inserted successfully.")
            else:
                print("No food found with that name.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error inserting user liked food: {e}")

    def insert_user_disliked_food(self, user_id, food_name):
        cursor = self.db.cursor()
        find_id_sql = """
        SELECT id FROM disliked_food WHERE name = %s;
        """
        insert_sql = """
        INSERT INTO user_disliked_food (user_id, disliked_food_id)
        VALUES (%s, %s);
        """
        try:
            cursor.execute(find_id_sql, (food_name,))
            result = cursor.fetchone()
            if result:
                food_id = result[0]
                cursor.execute(insert_sql, (user_id, food_id))
                self.db.commit()
                print("User disliked food inserted successfully.")
            else:
                print("No food found with that name.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error inserting user disliked food: {e}")
            
    import json

    # 1일치만 테스용
    # def insert_user_meal_plan(self, user_id, response, start_date, end_date=None):
    #     cursor = self.db.cursor()
    #     try:
    #         day = response["days"][0] 

    #         used_at = start_date

    #         breakfast_ids = [int(r["id"]) for r in day["recipes"] if r["meal_name"] == 'Breakfast']
    #         lunch_ids = [int(r["id"]) for r in day["recipes"] if r["meal_name"] == 'Lunch']
    #         dinner_ids = [
    #             int(r["id"])
    #             for r in day["recipes"]
    #             if r["meal_name"] in ("Dinner", "Main", "Side")
    #         ]
            
    #         snack_ids = [r["id"] for r in day["recipes"] if r["meal_name"] == "Snack"]
    #         snack1_id = snack_ids[0] if len(snack_ids) > 0 else None
    #         snack2_id = snack_ids[1] if len(snack_ids) > 1 else None
    #         snack3_id = snack_ids[2] if len(snack_ids) > 2 else None
            
    #         query = """
    #             INSERT INTO user_meal_plans (
    #                 user_id, created_at, used_at,
    #                 breakfast, snack_1, lunch, snack_2, dinner, snack_3
    #             ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    #         """
    #         cursor.execute(query, (
    #             user_id,
    #             start_date.date(),
    #             used_at.date(),
    #             json.dumps(breakfast_ids),
    #             snack1_id,
    #             json.dumps(lunch_ids),
    #             snack2_id,
    #             json.dumps(dinner_ids),
    #             snack3_id
    #         ))

    #         self.db.commit()

    #     except Exception as e:
    #         self.db.rollback()
    #         print(f"[ERROR] Inserting single-day meal plan for user {user_id}: {e}")

    #     finally:
    #         cursor.close()
      
    def insert_user_meal_plan(self, user_id, response, start_date, end_date):
        cursor = self.db.cursor()
        days = response["days"]
        try:
            for i, day in enumerate(days):
                used_at = start_date + datetime.timedelta(days=i)
                
                breakfast_ids = [int(r["id"]) for r in day["recipes"] if r["meal_name"] == 'Breakfast']
                lunch_ids = [int(r["id"]) for r in day["recipes"] if r["meal_name"] == 'Lunch']
                dinner_ids = [
                    int(r["id"])
                    for r in day["recipes"]
                    if r["meal_name"] in ("Dinner", "Main", "Side")
                ]
                
                snack_ids = [r["id"] for r in day["recipes"] if r["meal_name"] == "Snack"]
                snack1_id = snack_ids[0] if len(snack_ids) > 0 else None
                snack2_id = snack_ids[1] if len(snack_ids) > 1 else None
                snack3_id = snack_ids[2] if len(snack_ids) > 2 else None
                
                query = """
                    INSERT INTO user_meal_plans (
                        user_id, created_at, used_at,
                        breakfast, snack_1, lunch, snack_2, dinner, snack_3
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        breakfast = VALUES(breakfast),
                        snack_1 = VALUES(snack_1),
                        lunch = VALUES(lunch),
                        snack_2 = VALUES(snack_2),
                        dinner = VALUES(dinner),
                        snack_3 = VALUES(snack_3)
                """
                cursor.execute(query, (
                    user_id,
                    start_date.date(),
                    used_at.date(),
                    json.dumps(breakfast_ids),
                    snack1_id,
                    json.dumps(lunch_ids),
                    snack2_id,
                    json.dumps(dinner_ids),
                    snack3_id
                ))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"Error inserting meal plan for user {user_id}: {e}")
        finally:
            cursor.close()


    # ------------------- Update data -------------------
    def update_user_last_date_plan_profile(self, user_id, last_meal_plan_date):
        cursor = self.db.cursor()
        sql = """
        UPDATE user_profile
        SET last_meal_plan_date = %s
        WHERE user_id = %s;
        """
        values = (last_meal_plan_date, user_id)
        try:
            cursor.execute(sql, values)
            self.db.commit()
            print("User profile updated successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error updating user profile: {e}")

    # delete test data

    def delete_all_tables(self):
        cursor = self.db.cursor()
        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            for (table_name,) in tables:
                sql = f"DROP TABLE IF EXISTS `{table_name}`;"
                cursor.execute(sql)
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            self.db.commit()
            print("All tables deleted successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error deleting tables: {e}")

    # ------------------- retrieve data -------------------

    def get_user_profile(self, user_id):
        cursor = self.db.cursor()
        sql = "SELECT user_name, email, age, height, weight FROM user_profile WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()

        if result:
            user_profile = {
                "user_name": result[0],
                "email": result[1],
                "age": result[2],
                "height": result[3],
                "weight": result[4]
            }
            user_profile_json = json.dumps(user_profile)
            return user_profile_json
        else:
            return None

    def get_user_landing_page_profile(self, user_id):
        cursor = self.db.cursor()
        sql = "SELECT user_name, email, age, height, weight, activity_level, gender, selected_unit, health_goal FROM user_profile WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()

        if result:
            profile = {
                "user_name": result[0],
                "email": result[1],
                "age": result[2],
                "height": result[3],
                "weight": result[4],
                "activity_level": result[5],
                "gender": result[6],
                "selected_unit": result[7],
                "health_goal": result[8],
                "subscription_type_id": self.retrieve_user_subscription_type_id(user_id)
            }
            preference = {
                "allergies": self.retrieve_user_allergies(user_id),
                "likedFoods": self.retrieve_user_liked_food(user_id),
                "dislikedFoods": self.retrieve_user_disliked_food(user_id),
                "favouriteCuisines": self.retrieve_user_favourite_cuisines(user_id),
                "dietaryConstraint": self.retrieve_user_dieatary_constraints(user_id),
                "religiousConstraint": self.retrieve_user_religious_constraints(user_id),
                "snacks": self.retrieve_user_snack_preferences(user_id),
                "breakfasts": self.retrieve_user_breakfast_preferences(user_id)
            }
            user_info = {"profile": profile, "preference": preference}
            user_profile_json = json.dumps(user_info)
            return user_profile_json
        else:
            return None
        
    def get_all_subscribed_users(self):
        """
        Returns a list of user_ids who have a valid subscription
        """
        cursor = self.db.cursor()
        query = """
            SELECT us.user_id
            FROM user_subscription AS us
            JOIN user_profile AS up 
                ON up.user_id = us.user_id
            WHERE
                us.subscription_type_id IS NOT NULL
                AND (
                    us.subscription_type_id <> 1
                OR (us.subscription_type_id = 1 AND up.health_goal = 'lose_weight')
                )
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return [row[0] for row in results]

    # ------------------- look up table functions -------------------

    def get_allergy_ids(self, allergy_names):
        if not allergy_names:
            return []
        cursor = self.db.cursor()
        format_strings = ','.join(['%s'] * len(allergy_names))
        sql = f"SELECT id, name FROM allergies WHERE name IN ({format_strings})"
        cursor.execute(sql, tuple(allergy_names))
        result = cursor.fetchall()
        return {name: id for id, name in result}

    def update_user_allergies(self, user_id, allergies):
        allergy_ids = self.get_allergy_ids(allergies)
        cursor = self.db.cursor()

        delete_sql = "DELETE FROM user_allergies WHERE user_id = %s"
        try:
            cursor.execute(delete_sql, (user_id,))
            self.db.commit()
            print("Existing user allergies removed successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error removing user allergies: {e}")
            return

        values = [(user_id, allergy_ids[allergy])
                  for allergy in allergies if allergy in allergy_ids]
        insert_sql = "INSERT INTO user_allergies (user_id, allergy_id) VALUES (%s, %s)"

        try:
            if values:
                cursor.executemany(insert_sql, values)
                self.db.commit()
                print("User allergies added successfully.")
            else:
                print("No valid allergies provided for insertion.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error adding user allergies: {e}")

    def get_liked_food_ids(self, liked_food_names):
        if not liked_food_names:
            return []
        cursor = self.db.cursor()
        format_strings = ','.join(['%s'] * len(liked_food_names))
        sql = f"SELECT id, name FROM liked_food WHERE name IN ({format_strings})"
        cursor.execute(sql, tuple(liked_food_names))
        result = cursor.fetchall()
        return {name: id for id, name in result}

    def update_user_liked_foods(self, user_id, liked_food):
        liked_food_ids = self.get_liked_food_ids(liked_food)
        cursor = self.db.cursor()

        delete_sql = "DELETE FROM user_liked_food WHERE user_id = %s"
        try:
            cursor.execute(delete_sql, (user_id,))
            rows_deleted = cursor.rowcount
            self.db.commit()
            if rows_deleted > 0:
                print(
                    f"Existing user liked foods removed successfully, {rows_deleted} rows deleted.")
            else:
                print("No existing liked foods to remove.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error removing user liked foods: {e}")
            return
        values = [(user_id, liked_food_ids[food])
                  for food in liked_food if food in liked_food_ids]
        insert_sql = "INSERT INTO user_liked_food (user_id, liked_food_id) VALUES (%s, %s)"

        try:
            if values:
                cursor.executemany(insert_sql, values)
                self.db.commit()
                print("User liked foods added successfully.")
            else:
                print("No valid liked foods provided for insertion.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error adding user liked foods: {e}")

    def get_disliked_food_ids(self, disliked_food_names):
        if not disliked_food_names:
            return []
        cursor = self.db.cursor()
        format_strings = ','.join(['%s'] * len(disliked_food_names))
        sql = f"SELECT id, name FROM disliked_food WHERE name IN ({format_strings})"
        cursor.execute(sql, tuple(disliked_food_names))
        result = cursor.fetchall()
        return {name: id for id, name in result}

    def update_user_disliked_foods(self, user_id, disliked_food):
        disliked_food_ids = self.get_disliked_food_ids(disliked_food)
        cursor = self.db.cursor()

        delete_sql = "DELETE FROM user_disliked_food WHERE user_id = %s"
        try:
            cursor.execute(delete_sql, (user_id,))
            self.db.commit()
            print("Existing user disliked foods removed successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error removing user disliked foods: {e}")
            return

        values = [(user_id, disliked_food_ids[food])
                  for food in disliked_food if food in disliked_food_ids]
        insert_sql = "INSERT INTO user_disliked_food (user_id, disliked_food_id) VALUES (%s, %s)"
        try:
            if values:
                cursor.executemany(insert_sql, values)
                self.db.commit()
                print("User disliked foods added successfully.")
            else:
                print("No valid disliked foods provided for insertion.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error adding user disliked foods: {e}")

    def get_favourite_cuisine_ids(self, cuisine_names):
        if not cuisine_names:
            return []
        cursor = self.db.cursor()
        format_strings = ','.join(['%s'] * len(cuisine_names))
        sql = f"SELECT id, name FROM favourite_cuisines WHERE name IN ({format_strings})"
        cursor.execute(sql, tuple(cuisine_names))
        result = cursor.fetchall()
        return {name: id for id, name in result}

    def update_user_favourite_cuisines(self, user_id, cuisines):
        cuisine_ids = self.get_favourite_cuisine_ids(cuisines)
        cursor = self.db.cursor()
        delete_sql = "DELETE FROM user_favourite_cuisines WHERE user_id = %s"
        try:
            cursor.execute(delete_sql, (user_id,))
            self.db.commit()
            print("Existing user favourite cuisines removed successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error removing user favourite cuisines: {e}")
            return

        values = [(user_id, cuisine_ids[cuisine])
                  for cuisine in cuisines if cuisine in cuisine_ids]
        insert_sql = "INSERT INTO user_favourite_cuisines (user_id, cuisine_id) VALUES (%s, %s)"
        try:
            if values:
                cursor.executemany(insert_sql, values)
                self.db.commit()
                print("User favourite cuisines added successfully.")
            else:
                print("No valid cuisines provided for insertion.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error adding user favourite cuisines: {e}")
            
    def get_snack_ids(self, snack_names):
        if not snack_names:
            return []
        cursor = self.db.cursor()
        format_strings = ','.join(['%s'] * len(snack_names))
        sql = f"SELECT id, name FROM snacks WHERE name IN ({format_strings})"
        cursor.execute(sql, tuple(snack_names))
        result = cursor.fetchall()
        return {name: id for id, name in result}
    
    def update_user_prefered_snacks(self, user_id, snacks):
        snack_ids = self.get_snack_ids(snacks)
        cursor = self.db.cursor()
        delete_sql = "DELETE FROM user_snack_preferences WHERE user_id = %s"
        try:
            cursor.execute(delete_sql, (user_id,))
            self.db.commit()
            print("Existing user snack preference data removed.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error removing user snack preference: {e}")
            return

        values = [(user_id, snack_ids[snack])
                  for snack in snacks if snack in snack_ids]
        insert_sql = "INSERT INTO user_snack_preferences (user_id, snack_id) VALUES (%s, %s)"
        try:
            if values:
                cursor.executemany(insert_sql, values)
                self.db.commit()
                print("User favourite snack items added successfully.")
            else:
                print("No valid snack provided for insertion.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error adding user favourite snack items: {e}")
            
    def get_breakfast_ids(self, breakfast_names):
        if not breakfast_names:
            return []
        cursor = self.db.cursor()
        format_strings = ','.join(['%s'] * len(breakfast_names))
        sql = f"SELECT id, name FROM breakfasts WHERE name IN ({format_strings})"
        cursor.execute(sql, tuple(breakfast_names))
        result = cursor.fetchall()
        return {name: id for id, name in result}
    
    def update_user_prefered_breakfasts(self, user_id, breakfasts):
        breakfast_ids = self.get_breakfast_ids(breakfasts)
        cursor = self.db.cursor()
        delete_sql = "DELETE FROM user_breakfast_preferences WHERE user_id = %s"
        try:
            cursor.execute(delete_sql, (user_id,))
            self.db.commit()
            print("Existing user snack preference data removed.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error removing user snack preference: {e}")
            return

        values = [(user_id, breakfast_ids[breakfast])
                  for breakfast in breakfasts if breakfast in breakfast_ids]
        insert_sql = "INSERT INTO user_breakfast_preferences (user_id, breakfast_id) VALUES (%s, %s)"
        try:
            if values:
                cursor.executemany(insert_sql, values)
                self.db.commit()
                print("User favourite breakfast items added successfully.")
            else:
                print("No valid breakfast item provided for insertion.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error adding user favourite breakfast items: {e}")
            
            
# ----------------- Retrieve user data -----------------

    def retrieve_user_profile_json(self, user_id):
        cursor = self.db.cursor()
        print("user_id type:", type(user_id))  # Check the type of user_id
        sql = "SELECT age, weight, height, gender, activity_level FROM user_profile WHERE user_id = %s"
        print("sql:", sql)  # Print the SQL query for debugging
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        if result:
            profile_dict = {
                "age": result[0],
                "weight": result[1],
                "height": result[2],
                "gender": result[3],
                "activityLevel": result[4]
            }
            return profile_dict
        else:
            return None

    def retrieve_user_name(self, user_id):
        cursor = self.db.cursor()
        sql = "SELECT user_name FROM user_profile WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def retrieve_user_email(self, user_id):
        cursor = self.db.cursor()
        sql = "SELECT email FROM user_profile WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def retrieve_user_selected_unit(self, user_id):
        cursor = self.db.cursor()
        sql = "SELECT selected_unit FROM user_profile WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def retrieve_user_dieatary_constraints(self, user_id):
        cursor = self.db.cursor()
        sql = """
        SELECT dc.name
        FROM dietary_constraints dc
        JOIN user_dietary_constraints udc ON dc.id = udc.dietary_constraint_id
        WHERE udc.user_id = %s;
        """
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        return result[0].lower() if result else None

    def retrieve_user_health_goal(self, user_id):
        cursor = self.db.cursor()
        sql = "SELECT health_goal FROM user_profile WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def retrieve_user_religious_constraints(self, user_id):
        cursor = self.db.cursor()
        sql = """
        SELECT rc.name
        FROM religious_constraints rc
        JOIN user_religious_constraints urc ON rc.id = urc.religious_constraint_id
        WHERE urc.user_id = %s;
        """
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        return result[0].lower() if result else None

    def retrieve_user_liked_food(self, user_id):
        cursor = self.db.cursor()
        sql = """
        SELECT lf.name
        FROM liked_food lf
        JOIN user_liked_food ulf ON lf.id = ulf.liked_food_id
        WHERE ulf.user_id = %s;
        """
        cursor.execute(sql, (user_id,))
        result = cursor.fetchall()
        return [row[0] for row in result]

    def retrieve_user_disliked_food(self, user_id):
        cursor = self.db.cursor()
        sql = """
        SELECT df.name
        FROM disliked_food df
        JOIN user_disliked_food udf ON df.id = udf.disliked_food_id
        WHERE udf.user_id = %s;
        """
        cursor.execute(sql, (user_id,))
        result = cursor.fetchall()
        return [row[0] for row in result]

    def retrieve_user_favourite_cuisines(self, user_id):
        cursor = self.db.cursor()
        sql = """
        SELECT fc.name
        FROM favourite_cuisines fc
        JOIN user_favourite_cuisines ufc ON fc.id = ufc.cuisine_id
        WHERE ufc.user_id = %s;
        """
        cursor.execute(sql, (user_id,))
        result = cursor.fetchall()
        return [row[0] for row in result]

    def retrieve_user_allergies(self, user_id):
        cursor = self.db.cursor()
        sql = """
        SELECT a.name
        FROM allergies a
        JOIN user_allergies ua ON a.id = ua.allergy_id
        WHERE ua.user_id = %s;
        """
        cursor.execute(sql, (user_id,))
        result = cursor.fetchall()
        return [row[0] for row in result]
    
    def retrieve_user_snack_preferences(self, user_id):
        cursor = self.db.cursor()
        sql = """
        SELECT a.name
        FROM snacks a
        JOIN user_snack_preferences ua ON a.id = ua.snack_id
        WHERE ua.user_id = %s;
        """
        cursor.execute(sql, (user_id,))
        result = cursor.fetchall()
        return [row[0] for row in result]
    
    def retrieve_user_breakfast_preferences(self, user_id):
        cursor = self.db.cursor()
        sql = """
        SELECT a.name
        FROM breakfasts a
        JOIN user_breakfast_preferences ua ON a.id = ua.breakfast_id
        WHERE ua.user_id = %s;
        """
        cursor.execute(sql, (user_id,))
        result = cursor.fetchall()
        return [row[0] for row in result]

    def retrieve_user_last_date_plan_profile(self, user_id):
        cursor = self.db.cursor()
        sql = "SELECT last_meal_plan_date FROM user_profile WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def retrieve_user_id_and_emails_by_last_meal_plan_date(self, email_day):
        cursor = self.db.cursor()
        sql = """
        SELECT u.user_id, u.email
        FROM user_profile u
        WHERE DAYNAME(FROM_UNIXTIME(u.last_meal_plan_date / 1000)) = %s;
        """
        cursor.execute(sql, (email_day,))
        result = cursor.fetchall()
        return result

    def retrieve_user_subscription_type_id(self, user_id):
        cursor = self.db.cursor()
        sql = """
        SELECT subscription_type_id
        FROM user_subscription
        WHERE user_id = %s
        """
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

# ------------------- Validate User ----------------------

    def check_user_id_existence(self, user_id):
        cursor = self.db.cursor()
        sql = "SELECT user_id FROM user_profile WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        return True if result else False

    def check_user_subscription_validity(self, user_id):
        # If subscription_type_id is 3, then user is unscubscribed
        cursor = self.db.cursor()
        sql = "SELECT subscription_type_id FROM user_subscription WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        if result[0] == 1:
            return False
        return True


def instantiate_database():
    db = DatabaseManager()

    return db


if __name__ == '__main__':
    print("Running database manager")
    db = instantiate_database()
    print(db.get_user_landing_page_profile("100"))
