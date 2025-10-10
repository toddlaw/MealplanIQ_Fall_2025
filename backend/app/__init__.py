from flask import Flask, jsonify
from flask_cors import CORS
from user_db.user_db import DatabaseManager
from user_db.initiate_db import DatabaseSchemaManager
from app.routes_task import tasks_bp
from app.routes_recipe import bp as recipes_bp


app = Flask(__name__)


db = DatabaseManager.connect_to_database()
schema_manager = DatabaseSchemaManager(db)
schema_manager.create_all_tables()
schema_manager.populate_dictionary_tables()
app.register_blueprint(tasks_bp)
app.register_blueprint(recipes_bp) # Register the recipes blueprint

CORS(app)
from app import routes
