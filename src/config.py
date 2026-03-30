import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
        print("⚠️ Warning: GOOGLE_API_KEY not found in .env file")
    
    # Project Folders
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RAW_DATA = os.path.join(BASE_DIR, "data/raw")
    PROCESSED_DATA = os.path.join(BASE_DIR, "data/processed")

# Ensure folders exist
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)
