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


    # ------------------ Look-up tables ------------------

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
        constraints = ['None', 'Vegetarian', 'Vegan', 'Pescatarian']
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
        constraints = ['None', 'Halal', 'Kosher']
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
        allergies = ['None', 'Peanut', 'Gluten', 'Dairy', 'Grain', 'Seafood',
                     'Sesame', 'Shellfish', 'Soy', 'Egg', 'Sulfite', 'Tree Nut', 'Wheat']
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
        cuisines = ['None', 'American', 'Italian', 'Mexican',
                    'Japanese', 'Indian', 'Greek', 'Chinese']
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
        liked_foods = ['None', 'Pizza', 'Burger',
                       'Pasta', 'Sushi', 'Salad', 'Ice Cream']
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
        disliked_foods = ['None', 'Anchovies', 'Olives',
                          'Cilantro', 'Blue Cheese', 'Liver', 'Tofu']
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