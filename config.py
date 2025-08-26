import os
from dotenv import load_dotenv

# load .env file
load_dotenv()

# fetch API key from env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Paths
DB_PATH = os.environ.get("FAA_DB", "faa.sqlite")
DATA_DIR = os.environ.get("FAA_DATA_DIR", "/Users/kaushikdas/Sparkov_Data_Generation/synthetic_data")
ARTIFACT_DIR = os.environ.get("FAA_ARTIFACTS", "artifacts")

# Models
MODEL_BRAIN = os.environ.get("FAA_MODEL_BRAIN", "gpt-4o-mini")
MODEL_VISION = os.environ.get("FAA_MODEL_VISION", "gpt-4o")

# OpenAI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

from openai import OpenAI

def get_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise RuntimeError("Set OPENAI_API_KEY in your environment or .env file.")
    return OpenAI(api_key=OPENAI_API_KEY)