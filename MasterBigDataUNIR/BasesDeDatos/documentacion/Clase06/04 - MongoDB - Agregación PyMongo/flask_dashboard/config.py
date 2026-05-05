# Autor: Marlon Cárdenas (@mCardenas) - 2025

import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=False)

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "LabTestDB")
APP_NAME = os.getenv("APP_NAME", "Mongo Dashboard")
