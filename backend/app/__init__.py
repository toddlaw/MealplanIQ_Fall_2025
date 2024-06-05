from flask import Flask, jsonify
from flask_apscheduler import APScheduler
from flask_cors import CORS


app = Flask(__name__)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

CORS(app)
from app import routes
