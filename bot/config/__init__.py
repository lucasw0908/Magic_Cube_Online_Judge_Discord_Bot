import os
import json
from dotenv import load_dotenv


load_dotenv()

BASEDIR = os.path.dirname(__file__)
SETTINGS = json.load(open(os.path.join(BASEDIR, "settings.json"), "r"))

# Environment Variables
TOKEN = os.getenv("TOKEN")
SQL_URL = os.getenv("SQL_URL") or "sqlite:///db.sqlite3"

# Bot Settings
LOCALE = SETTINGS["LOCALE"]
LOG_FILENAME = SETTINGS["LOG_FILENAME"]

# Judge Settings
TIME_LIMIT = SETTINGS["TIME_LIMIT"]
CUBE_SIZE = SETTINGS["CUBE_SIZE"]