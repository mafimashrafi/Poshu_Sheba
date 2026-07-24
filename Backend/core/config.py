import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMMA_MODEL = "models/gemma-4-26b-a4b-it"