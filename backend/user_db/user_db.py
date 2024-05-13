import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def connect_to_database():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        charset='utf8'
    )


    # return pymysql.connect(
    #     host='localhost',
    #     user='root',
    #     password='password12',
    #     database='mealPlan',
    #     charset='utf8'
    # )

def create_user_profile_table(db):
    # db = connect_to_database()
    cursor = db.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS user_profile (
        user_id INT PRIMARY KEY,
        gender VARCHAR(255),
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
        db.commit()
        print("Table created successfully")
    except pymysql.Error as e:
        db.rollback()
        print(f"Error creating table: {e}")
    finally:
        db.close()

def create_dietary_constraints(db):
    cursor = db.cursor()
    create_dietary_constraints_table_sql = """
    CREATE TABLE IF NOT EXISTS dietary_constraints (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE
    );
    """
    try:
        cursor.execute(create_dietary_constraints_table_sql)
        db.commit()
        print("Table created successfully")
    except pymysql.Error as e:
        db.rollback()
        print(f"Error creating table: {e}")
    finally:
        db.close()

def create_religious_constraints(db):
    cursor = db.cursor()
    sql = """
    CREATE TABLE IF NOT EXISTS religious_constraints (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE
    );
    """
    try:
        cursor.execute(sql)
        db.commit()
        print("Religious constraints table created successfully.")
    except pymysql.Error as e:
        db.rollback()
        print(f"Error creating religious constraints table: {e}")
    finally:
        db.close()

def create_allergies(db):
    cursor = db.cursor()
    sql = """
    CREATE TABLE IF NOT EXISTS allergies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE
    );
    """
    try:
        cursor.execute(sql)
        db.commit()
        print("Allergies table created successfully.")
    except pymysql.Error as e:
        db.rollback()
        print(f"Error creating allergies table: {e}")
    finally:
        db.close()

def create_favourite_cuisines(db):
    cursor = db.cursor()
    create_cuisines_sql = """
    CREATE TABLE IF NOT EXISTS favourite_cuisines (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE
    );
    """
    try:
        cursor.execute(create_cuisines_sql)
        db.commit()
        print("Cuisines table created successfully.")
    except pymysql.Error as e:
        db.rollback()
        print(f"Error creating cuisines table: {e}")
    finally:
        db.close()

# Look-up tables
def create_user_dietary_constraints(db):
    cursor = db.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS user_dietary_constraints (
        user_id INT,
        dietary_constraint_id INT,
        PRIMARY KEY (user_id, dietary_constraint_id),
        FOREIGN KEY (user_id) REFERENCES user_profile(user_id),
        FOREIGN KEY (dietary_constraint_id) REFERENCES dietary_constraints(id)
    );
    """
    try:
        cursor.execute(create_table_sql)
        db.commit()
        print("User dietary constraints table created successfully.")
    except pymysql.Error as e:
        db.rollback()
        print(f"Error creating user dietary constraints table: {e}")
    finally:
        db.close()

def create_user_religious_constraints(db):
    cursor = db.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS user_religious_constraints (
        user_id INT,
        religious_constraint_id INT,
        PRIMARY KEY (user_id, religious_constraint_id),
        FOREIGN KEY (user_id) REFERENCES user_profile(user_id),
        FOREIGN KEY (religious_constraint_id) REFERENCES religious_constraints(id)
    );
    """
    try:
        cursor.execute(create_table_sql)
        db.commit()
        print("User religious constraints table created successfully.")
    except pymysql.Error as e:
        db.rollback()
        print(f"Error creating user religious constraints table: {e}")
    finally:
        db.close()
        
def create_user_favourite_cuisines(db):
    cursor = db.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS user_favourite_cuisines (
        user_id INT,
        cuisine_id INT,
        PRIMARY KEY (user_id, cuisine_id),
        FOREIGN KEY (user_id) REFERENCES user_profile(user_id),
        FOREIGN KEY (cuisine_id) REFERENCES favourite_cuisines(id)
    );
    """
    try:
        cursor.execute(create_table_sql)
        db.commit()
        print("User favourite cuisines table created successfully.")
    except pymysql.Error as e:
        db.rollback()
        print(f"Error creating user favourite cuisines table: {e}")
    finally:
        db.close()


def create_user_allergies(db):
    cursor = db.cursor()
    sql = """
    CREATE TABLE IF NOT EXISTS user_allergies (
        user_id INT,
        allergy_id INT,
        PRIMARY KEY (user_id, allergy_id),
        FOREIGN KEY (user_id) REFERENCES user_profile(user_id),
        FOREIGN KEY (allergy_id) REFERENCES allergies(id)
    );
    """
    try:
        cursor.execute(sql)
        db.commit()
        print("User allergies table created successfully.")
    except pymysql.Error as e:
        db.rollback()
        print(f"Error creating user allergies table: {e}")
    finally:
        db.close()

def create_and_populate_subscription_status_table():
    db = connect_to_database()
    cursor = db.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS subscription_status (
        subscription_type_id INT PRIMARY KEY,
        subscription_type VARCHAR(255) NOT NULL
    );
    """
    populate_table_sql = """
    INSERT INTO subscription_status (subscription_type_id, subscription_type) VALUES
    (1, 'monthly_subscription'),
    (2, 'yearly_subscription'),
    (3, 'free_trial');
    """
    try:
        cursor.execute(create_table_sql)
        db.commit()
        print("Table created successfully")
        cursor.execute(populate_table_sql)
        db.commit()
        print("Subscription statuses added successfully")
    except pymysql.Error as e:
        db.rollback()
        print(f"Error in database operation: {e}")
    finally:
        db.close()

def create_user_subscription_table():
    db = connect_to_database()
    cursor = db.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS user_subscription (
        user_id INT PRIMARY KEY,
        subscription_type_id INT,
        subscription_stripe_id INT,
        subscription_expiry_date DATE,
        FOREIGN KEY (user_id) REFERENCES user_profile(user_id),
        FOREIGN KEY (subscription_type_id) REFERENCES subscription_status(subscription_type_id)
    );
    """
    try:
        cursor.execute(create_table_sql)
        db.commit()
        print("User subscription table created successfully.")
    except pymysql.Error as e:
        db.rollback()
        print(f"Error creating user subscription table: {e}")
    finally:
        db.close()

 # Initiate tables
def populate_dietary_constraints_table():
    db = connect_to_database()
    cursor = db.cursor()
    sql = """
    INSERT INTO dietary_constraints (name) VALUES
    ('None'),
    ('Vegan'),
    ('Pescatarian')
    """
    try:
        cursor.execute(sql)
        db.commit()
        print("Dietary constraints added successfully.")
    except pymysql.Error as e:
        db.rollback()
        print(f"Error adding dietary constraints: {e}")
    finally:
        cursor.close()

def populate_religious_constraints_table():
    db = connect_to_database()
    cursor = db.cursor()
    sql = """
    INSERT INTO religious_constraints (name) VALUES
    ('None'),
    ('Halal'),
    ('Kosher')
    """
    try:
        cursor.execute(sql)
        db.commit()
        print("Religious constraints added successfully.")
    except pymysql.Error as e:
        db.rollback()
        print(f"Error adding religious constraints: {e}")
    finally:
        cursor.close()

def populate_allergies_table():
    db = connect_to_database()
    cursor = db.cursor()
    sql = """
    INSERT INTO allergies (name) VALUES
    ('None'),
    ('Peanuts'),
    ('Gluten'),
    ('Dairy')
    """
    try:
        cursor.execute(sql)
        db.commit()
        print("Allergies added successfully.")
    except pymysql.Error as e:
        db.rollback()
        print(f"Error adding allergies: {e}")
    finally:
        cursor.close()


# Test functions
def test_insert_user_profile(db):
    cursor = db.cursor()
    sql = """
    INSERT INTO user_profile (user_id, gender, height, age, weight, activity_level, selected_unit, health_goal)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """
    values = (1, 'Male', 174.0, 34, 65.0, 'Sedentary', 'metric', 'Lose weight')
    try:
        cursor.execute(sql, values)
        db.commit()
        print("User profile inserted successfully.")
    except pymysql.Error as e:
        db.rollback()
        print(f"Error inserting user profile: {e}")
    finally:
        cursor.close()


# delete test data
def delete_all_tables(db):
    cursor = db.cursor()
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        for (table_name,) in tables:
            sql = f"DROP TABLE IF EXISTS `{table_name}`;"
            cursor.execute(sql)
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        db.commit()
        print("All tables deleted successfully.")
    except pymysql.Error as e:
        db.rollback()
        print(f"Error deleting tables: {e}")
    finally:
        cursor.close()

if __name__ == '__main__':
    db = connect_to_database()
    # create_user_profile_table(db)
    # test_insert_user_profile(db)

