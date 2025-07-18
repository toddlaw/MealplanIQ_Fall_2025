import pymysql

class DatabaseSchemaManager:
    def __init__(self, db_connection):
        self.db = db_connection

    def create_all_tables(self):
        print("===== Creating all tables =====")
        self.create_user_profile_table()
        self.create_dietary_constraints()
        self.create_religious_constraints()
        self.create_allergies()
        self.create_favourite_cuisines()
        self.create_liked_food()
        self.create_disliked_food()

        self.create_user_dietary_constraints()
        self.create_user_religious_constraints()
        self.create_user_favourite_cuisines()
        self.create_user_allergies()
        self.create_user_liked_food()
        self.create_user_disliked_food()
        self.create_snacks()
        self.create_breakfasts()
        self.create_user_breakfast_preferences()
        self.create_user_snack_preferences()
    
        self.create_meal_plans()
        self.create_nutrition_plans()

        self.create_and_populate_subscription_status_table()
        self.create_user_subscription_table()
        

        print("===== All tables created successfully =====")

    def populate_dictionary_tables(self):
        print("===== Populating dictionary tables =====")
        self.populate_dietary_constraints_table()
        self.populate_religious_constraints_table()
        self.populate_allergies_table()
        self.populate_favourite_cuisines_table()
        self.populate_liked_food_table()
        self.populate_disliked_food_table()
        self.populate_snacks_table()
        self.populate_breakfasts_table()
        print("===== Dictionary tables populated successfully =====")

    def create_user_profile_table(self):
        cursor = self.db.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS user_profile (
            user_id VARCHAR(255) PRIMARY KEY,
            user_name VARCHAR(255),
            email VARCHAR(255),
            gender VARCHAR(255),
            last_meal_plan_date BIGINT,
            height DOUBLE,
            age INT,
            weight DOUBLE,
            activity_level VARCHAR(255),
            selected_unit VARCHAR(255),
            health_goal VARCHAR(255)
        );
        """
        try:
            cursor.execute(create_table_sql)
            self.db.commit()
            print("User profile table created successfully")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating table: {e}")

    def create_dietary_constraints(self):
        cursor = self.db.cursor()
        create_dietary_constraints_table_sql = """
        CREATE TABLE IF NOT EXISTS dietary_constraints (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE
        );
        """
        try:
            cursor.execute(create_dietary_constraints_table_sql)
            self.db.commit()
            print("Dietary constraint table created successfully")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating table: {e}")

    def create_religious_constraints(self):
        cursor = self.db.cursor()
        sql = """
        CREATE TABLE IF NOT EXISTS religious_constraints (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE
        );
        """
        try:
            cursor.execute(sql)
            self.db.commit()
            print("Religious constraints table created successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating religious constraints table: {e}")

    def create_allergies(self):
        cursor = self.db.cursor()
        sql = """
        CREATE TABLE IF NOT EXISTS allergies (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE
        );
        """
        try:
            cursor.execute(sql)
            self.db.commit()
            print("Allergies table created successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating allergies table: {e}")

    def create_favourite_cuisines(self):
        cursor = self.db.cursor()
        create_cuisines_sql = """
        CREATE TABLE IF NOT EXISTS favourite_cuisines (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE
        );
        """
        try:
            cursor.execute(create_cuisines_sql)
            self.db.commit()
            print("Cuisines table created successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating cuisines table: {e}")

    def create_liked_food(self):
        cursor = self.db.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS liked_food (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE
        );
        """
        try:
            cursor.execute(create_table_sql)
            self.db.commit()
            print("Food table created successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating food table: {e}")

    def create_disliked_food(self):
        cursor = self.db.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS disliked_food (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE
        );
        """
        try:
            cursor.execute(create_table_sql)
            self.db.commit()
            print("Disliked food table created successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating disliked food table: {e}")


    def create_user_dietary_constraints(self):
        cursor = self.db.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS user_dietary_constraints (
            user_id VARCHAR(255),
            dietary_constraint_id INT,
            PRIMARY KEY (user_id, dietary_constraint_id),
            FOREIGN KEY (user_id) REFERENCES user_profile(user_id),
            FOREIGN KEY (dietary_constraint_id) REFERENCES dietary_constraints(id)
        );
        """
        try:
            cursor.execute(create_table_sql)
            self.db.commit()
            print("User dietary constraints table created successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating user dietary constraints table: {e}")

    def create_user_religious_constraints(self):
        cursor = self.db.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS user_religious_constraints (
            user_id VARCHAR(255),
            religious_constraint_id INT,
            PRIMARY KEY (user_id, religious_constraint_id),
            FOREIGN KEY (user_id) REFERENCES user_profile(user_id),
            FOREIGN KEY (religious_constraint_id) REFERENCES religious_constraints(id)
        );
        """
        try:
            cursor.execute(create_table_sql)
            self.db.commit()
            print("User religious constraints table created successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating user religious constraints table: {e}")

    def create_user_favourite_cuisines(self):
        cursor = self.db.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS user_favourite_cuisines (
            user_id VARCHAR(255),
            cuisine_id INT,
            PRIMARY KEY (user_id, cuisine_id),
            FOREIGN KEY (user_id) REFERENCES user_profile(user_id),
            FOREIGN KEY (cuisine_id) REFERENCES favourite_cuisines(id)
        );
        """
        try:
            cursor.execute(create_table_sql)
            self.db.commit()
            print("User favourite cuisines table created successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating user favourite cuisines table: {e}")

    def create_user_allergies(self):
        cursor = self.db.cursor()
        sql = """
        CREATE TABLE IF NOT EXISTS user_allergies (
            user_id VARCHAR(255),
            allergy_id INT,
            PRIMARY KEY (user_id, allergy_id),
            FOREIGN KEY (user_id) REFERENCES user_profile(user_id),
            FOREIGN KEY (allergy_id) REFERENCES allergies(id)
        );
        """
        try:
            cursor.execute(sql)
            self.db.commit()
            print("User allergies table created successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating user allergies table: {e}")

    def create_user_liked_food(self):
        cursor = self.db.cursor()
        sql = """
        CREATE TABLE IF NOT EXISTS user_liked_food (
            user_id VARCHAR(255),
            liked_food_id INT,
            PRIMARY KEY (user_id, liked_food_id),
            FOREIGN KEY (user_id) REFERENCES user_profile(user_id),
            FOREIGN KEY (liked_food_id) REFERENCES liked_food(id)
        );
        """
        try:
            cursor.execute(sql)
            self.db.commit()
            print("User liked food table created successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating user liked food table: {e}")

    def create_user_disliked_food(self):
        cursor = self.db.cursor()
        sql = """
        CREATE TABLE IF NOT EXISTS user_disliked_food (
            user_id VARCHAR(255),
            disliked_food_id INT,
            PRIMARY KEY (user_id, disliked_food_id),
            FOREIGN KEY (user_id) REFERENCES user_profile(user_id),
            FOREIGN KEY (disliked_food_id) REFERENCES disliked_food(id)
        );
        """
        try:
            cursor.execute(sql)
            self.db.commit()
            print("User disliked food table created successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating user disliked food table: {e}")


    def create_user_subscription_table(self):
        cursor = self.db.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS user_subscription (
            user_id VARCHAR(255) PRIMARY KEY,
            subscription_type_id INT,
            stripe_customer_id VARCHAR(255),
            subscription_stripe_id VARCHAR(255),
            subscription_expiry_date DATE,
            FOREIGN KEY (user_id) REFERENCES user_profile(user_id),
            FOREIGN KEY (subscription_type_id) REFERENCES subscription_status(subscription_type_id)
        );
        """
        try:
            cursor.execute(create_table_sql)
            self.db.commit()
            print("User subscription table created successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating user subscription table: {e}")

    def create_snacks(self):
        cursor = self.db.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS snacks (
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(20) UNIQUE
        );
        """
        try:
            cursor.execute(create_table_sql)
            self.db.commit()
            print("Snack preferences table created successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating snack preferences table: {e}")
        finally:
            cursor.close()

    def create_user_snack_preferences(self):
        cursor = self.db.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS user_snack_preferences (
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(255),
            snack_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES user_profile(user_id),
            FOREIGN KEY(snack_id) REFERENCES snacks(id)
        );
        """
        try:
            cursor.execute(create_table_sql)
            self.db.commit()
            print("user_snack_preferences table created successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating user_snack_preferences table: {e}")
        finally:
            cursor.close()       

    def create_user_breakfast_preferences(self):
        cursor = self.db.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS user_breakfast_preferences (
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(255),
            breakfast_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES user_profile(user_id),
            FOREIGN KEY(breakfast_id) REFERENCES breakfasts(id)
        );
        """
        try:
            cursor.execute(create_table_sql)
            self.db.commit()
            print("user_breakfast_preferences table created successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating user_breakfast_preferences table: {e}")
        finally:
            cursor.close()


    # Create breakfast look-up table(ENUM)
    def create_breakfasts(self):
        cursor = self.db.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS breakfasts (
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(20) UNIQUE
        );
        """
        try:
            cursor.execute(create_table_sql)
            self.db.commit()
            print("Breakfast preferences table created successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating breakfast preferences table: {e}")
        finally:
            cursor.close()

    def create_meal_plans(self):
        cursor = self.db.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS user_meal_plans (
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(255),
            created_at DATE,
            used_at DATE,
            breakfast INTEGER[],
            snack_1 INTEGER,
            lunch INTEGER[],
            snack_2 INTEGER,
            dinner INTEGER[],
            snack_3 INTEGER,
            FOREIGN KEY(user_id) REFERENCES user_profile(user_id)
        );
        """
        try:
            cursor.execute(create_table_sql)
            self.db.commit()
            print("user_meal_plans table created successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating user_meal_plans table: {e}")
        finally:
            cursor.close()

    def create_nutrition_plans(self):
        cursor = self.db.cursor()
        create_table_sql = """
        CREATE TABLE user_weekly_nutrition (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,

            energy_kcal_actual FLOAT,
            energy_kcal_target FLOAT,
            fiber_g_actual FLOAT,
            fiber_g_target FLOAT,
            carbohydrates_g_actual FLOAT,
            carbohydrates_g_target FLOAT,
            protein_g_actual FLOAT,
            protein_g_target FLOAT,
            fats_g_actual FLOAT,
            fats_g_target FLOAT,
            calcium_mg_actual FLOAT,
            calcium_mg_target FLOAT,
            sodium_mg_actual FLOAT,
            sodium_mg_target FLOAT,
            copper_mg_actual FLOAT,
            copper_mg_target FLOAT,
            fluoride_mg_actual FLOAT,
            fluoride_mg_target FLOAT,
            iron_mg_actual FLOAT,
            iron_mg_target FLOAT,
            magnesium_mg_actual FLOAT,
            magnesium_mg_target FLOAT,
            manganese_mg_actual FLOAT,
            manganese_mg_target FLOAT,
            potassium_mg_actual FLOAT,
            potassium_mg_target FLOAT,
            selenium_ug_actual FLOAT,
            selenium_ug_target FLOAT,
            zinc_mg_actual FLOAT,
            zinc_mg_target FLOAT,
            vitamin_a_iu_actual FLOAT,
            vitamin_a_iu_target FLOAT,
            thiamin_mg_actual FLOAT,
            thiamin_mg_target FLOAT,
            riboflavin_mg_actual FLOAT,
            riboflavin_mg_target FLOAT,
            niacin_mg_actual FLOAT,
            niacin_mg_target FLOAT,
            vitamin_b5_mg_actual FLOAT,
            vitamin_b5_mg_target FLOAT,
            vitamin_b6_mg_actual FLOAT,
            vitamin_b6_mg_target FLOAT,
            vitamin_b12_ug_actual FLOAT,
            vitamin_b12_ug_target FLOAT,
            folate_ug_actual FLOAT,
            folate_ug_target FLOAT,
            vitamin_c_mg_actual FLOAT,
            vitamin_c_mg_target FLOAT,
            vitamin_d_iu_actual FLOAT,
            vitamin_d_iu_target FLOAT,
            vitamin_e_mg_actual FLOAT,
            vitamin_e_mg_target FLOAT,
            choline_mg_mg_actual FLOAT,
            choline_mg_mg_target FLOAT,
            vitamin_k_ug_actual FLOAT,
            vitamin_k_ug_target FLOAT,
        );

        """
        try:
            cursor.execute(create_table_sql)
            self.db.commit()
            print("user_weekly_nutrition table created successfully.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error creating user_weekly_nutrition table: {e}")
        finally:
            cursor.close()


    # ------------------ Look-up tables ------------------

    def populate_breakfasts_table(self):
        cursor = self.db.cursor()
        breakfast_items = [
            'bagel',
            'cereal',
            'coffee',
            'cream of wheat',
            'hashbrown',
            'juice',
            'oatmeal',
            'pancake',
            'toast',
            'waffle'
        ]

        try:
            for item in breakfast_items:
                cursor.execute(
                    "SELECT name FROM breakfasts WHERE name = %s", (item,)
                )
                result = cursor.fetchone()
                if not result:
                    try:
                        cursor.execute(
                            "INSERT INTO breakfasts (name) VALUES (%s)", (item,)
                        )
                        self.db.commit()
                        print(f"{item} added successfully.")
                    except pymysql.Error as e:
                        self.db.rollback()
                        print(f"Error adding breakfast preference {item}: {e}")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error in database operation: {e}")
        finally:
            cursor.close()


    def populate_snacks_table(self):
        cursor = self.db.cursor()
        snacks = [
            'berries',
            'cracker',
            'dried fruit',
            'fruit',
            'nut',
            'snack bar',
            'trail mix',
            'veggies and dips',
            'yogurt'
        ]

        try:
            for snack in snacks:
                cursor.execute(
                    "SELECT name FROM snacks WHERE name = %s", (snack,)
                )
                result = cursor.fetchone()
                if not result:
                    try:
                        cursor.execute(
                            "INSERT INTO snacks (name) VALUES (%s)", (snack,)
                        )
                        self.db.commit()
                        print(f"{snack} added successfully.")
                    except pymysql.Error as e:
                        self.db.rollback()
                        print(f"Error adding snack preference {snack}: {e}")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error in database operation: {e}")
        finally:
            cursor.close()




    def create_and_populate_subscription_status_table(self):
        cursor = self.db.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS subscription_status (
            subscription_type_id INT PRIMARY KEY,
            subscription_type VARCHAR(255) NOT NULL
        );
        """
        subscription_types = [
            (1, 'free_trial'),
            (2, 'paid_trial'),
            (3, 'monthly_subscription'),
            (4, 'quarterly_subscription'),
            (5, 'yearly_subscription')
        ]
        try:
            cursor.execute(create_table_sql)
            self.db.commit()
            print("Subscription table created successfully")
            for subscription_type_id, subscription_type in subscription_types:
                cursor.execute(
                    "SELECT subscription_type_id FROM subscription_status WHERE subscription_type_id = %s", (subscription_type_id,))
                result = cursor.fetchone()
                if not result:
                    cursor.execute("INSERT INTO subscription_status (subscription_type_id, subscription_type) VALUES (%s, %s)", (
                        subscription_type_id, subscription_type))
                    self.db.commit()
                    print(
                        f"Subscription status {subscription_type} added successfully.")
                else:
                    print(
                        f"Subscription status {subscription_type} already exists.")
        except pymysql.Error as e:
            self.db.rollback()
            print(f"Error in database operation: {e}")



    def populate_dietary_constraints_table(self):
        cursor = self.db.cursor()
        constraints = ['none', 'vegetarian', 'vegan', 'pescatarian']
        for constraint in constraints:
            cursor.execute(
                "SELECT name FROM dietary_constraints WHERE name = %s", (constraint,))
            result = cursor.fetchone()
            if not result:
                try:
                    cursor.execute(
                        "INSERT INTO dietary_constraints (name) VALUES (%s)", (constraint,))
                    self.db.commit()
                    print(f"{constraint} added successfully.")
                except pymysql.Error as e:
                    self.db.rollback()
                    print(f"Error adding dietary constraint {constraint}: {e}")
        cursor.close()

    def populate_religious_constraints_table(self):
        cursor = self.db.cursor()
        constraints = ['none', 'halal', 'kosher']
        for constraint in constraints:
            cursor.execute(
                "SELECT name FROM religious_constraints WHERE name = %s", (constraint,))
            result = cursor.fetchone()
            if not result:
                try:
                    cursor.execute(
                        "INSERT INTO religious_constraints (name) VALUES (%s)", (constraint,))
                    self.db.commit()
                    print(f"{constraint} added successfully.")
                except pymysql.Error as e:
                    self.db.rollback()
                    print(
                        f"Error adding religious constraint {constraint}: {e}")
        cursor.close()

    def populate_allergies_table(self):
        cursor = self.db.cursor()
        allergies = ['peanut', 'gluten', 'dairy', 'grain', 'seafood',
                     'sesame', 'shellfish', 'soy', 'egg', 'sulfite', 'tree nut', 'wheat']
        for allergy in allergies:
            cursor.execute(
                "SELECT name FROM allergies WHERE name = %s", (allergy,))
            result = cursor.fetchone()
            if not result:
                try:
                    cursor.execute(
                        "INSERT INTO allergies (name) VALUES (%s)", (allergy,))
                    self.db.commit()
                    print(f"{allergy} added successfully.")
                except pymysql.Error as e:
                    self.db.rollback()
                    print(f"Error adding allergy {allergy}: {e}")
        cursor.close()

    def populate_favourite_cuisines_table(self):
        cursor = self.db.cursor()
        cuisines = ['american', 'chinese', 'japanese', 'korean', 'french', 'italian', 'mexican']
        for cuisine in cuisines:
            cursor.execute(
                "SELECT name FROM favourite_cuisines WHERE name = %s", (cuisine,))
            result = cursor.fetchone()
            if not result:
                try:
                    cursor.execute(
                        "INSERT INTO favourite_cuisines (name) VALUES (%s)", (cuisine,))
                    self.db.commit()
                except Exception as e:
                    print(f"Failed to insert {cuisine}: {e}")
        cursor.close()

    def populate_liked_food_table(self):
        cursor = self.db.cursor()
        liked_foods = ['pizza', 'burger', 'pasta', 'sushi', 'salad']
        for food in liked_foods:
            cursor.execute(
                "SELECT name FROM liked_food WHERE name = %s", (food,))
            result = cursor.fetchone()
            if not result:
                try:
                    cursor.execute(
                        "INSERT INTO liked_food (name) VALUES (%s)", (food,))
                    self.db.commit()
                    print(f"{food} added successfully.")
                except pymysql.Error as e:
                    self.db.rollback()
                    print(f"Error adding liked food {food}: {e}")
        cursor.close()

    def populate_disliked_food_table(self):
        cursor = self.db.cursor()
        disliked_foods = ['anchovies', 'olive', 'cilantro', 'blue cheese', 'liver', 'tofu']
        for food in disliked_foods:
            # Check if the food already exists
            cursor.execute(
                "SELECT name FROM disliked_food WHERE name = %s", (food,))
            result = cursor.fetchone()
            if not result:
                try:
                    # Insert the food if it does not exist
                    cursor.execute(
                        "INSERT INTO disliked_food (name) VALUES (%s)", (food,))
                    self.db.commit()
                    print(f"{food} added successfully.")
                except pymysql.Error as e:
                    self.db.rollback()
                    print(f"Error adding disliked food {food}: {e}")
        cursor.close()