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

def create_user_profile_table():
    db = connect_to_database()
    cursor = db.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS user_profile (
        user_id INT PRIMARY KEY,
        gender VARCHAR(255),
        height double,
        age INT,
        weight double,
        activity_level VARCHAR(255),
        subscription_status VARCHAR(255),
        subscription_id VARCHAR(255)
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

def create_and_populate_subscription_status_table():
    db = connect_to_database()
    cursor = db.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS subscription_status (
        subscription_id INT PRIMARY KEY,
        subscription_status VARCHAR(255) NOT NULL
    );
    """
    populate_table_sql = """
    INSERT INTO subscription_status (subscription_id, subscription_status) VALUES
    (1, 'monthly_subscription'),
    (2, 'yearly_subscription'),
    (3, 'free_trial')
    ON DUPLICATE KEY UPDATE subscription_status=VALUES(subscription_status);
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



def delete_all_user_profiles():
    db = connect_to_database()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM user_profile;")
        db.commit()
        print("Data deleted successfully from user_profile")
    except pymysql.Error as e:
        db.rollback()
        print(f"Error deleting data: {e}")
    finally:
        db.close()


def save_user_profile(user_id, gender, height, age, weight, activity_level, subscription_status="", subscription_id=""):
    db = connect_to_database()
    cursor = db.cursor()
    insert_sql = """
    INSERT INTO user_profile (user_id, gender, height, age, weight, activity_level, subscription_status, subscription_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """
    try:
        cursor.execute(insert_sql, (user_id, gender, height, age, weight, activity_level, subscription_status, subscription_id))
        db.commit()
        print("User profile saved successfully")
    except pymysql.Error as e:
        db.rollback()
        print(f"Error saving user profile: {e}")
    finally:
        db.close()



if __name__ == '__main__':
    create_user_profile_table()
    create_and_populate_subscription_status_table()
