import os
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load the repository's .env, resolving it relative to this file (Backend/core/config.py -> parents[2] is repository root)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")
