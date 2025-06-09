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

    def update_user_profile_from_dashboard(self, user_name, email, age,  gender, height, weight, activity_level, user_id):
        cursor = self.db.cursor()
        sql = """
        UPDATE user_profile
        SET user_name = %s, gender = %s, height = %s, age = %s, weight = %s, activity_level = %s, email = %s
        WHERE user_id = %s;
        """
        values = (user_name, gender, height, age,
                  weight, activity_level, email, user_id)
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
        sql = "SELECT user_name, email, age, height, weight, activity_level, gender, selected_unit FROM user_profile WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()

        if result:
            user_profile = {
                "user_name": result[0],
                "email": result[1],
                "age": result[2],
                "height": result[3],
                "weight": result[4],
                "activity_level": result[5],
                "gender": result[6],
                "selected_unit": result[7]
            }
            user_profile_json = json.dumps(user_profile)
            return user_profile_json
        else:
            return None

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
        result = cursor.fetchall()
        return [row[0] for row in result]

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
        result = cursor.fetchall()
        return [row[0] for row in result]

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
