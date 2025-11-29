import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
