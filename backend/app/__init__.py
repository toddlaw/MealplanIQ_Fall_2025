from flask import Flask, jsonify
from flask_apscheduler import APScheduler
from flask_cors import CORS
from user_db.user_db import DatabaseManager
from user_db.initiate_db import DatabaseSchemaManager



app = Flask(__name__)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

db = DatabaseManager.connect_to_database()
schema_manager = DatabaseSchemaManager(db)
schema_manager.create_all_tables()

CORS(app)
from app import routes
