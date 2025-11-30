import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    # 1st key (jo tumne OPENAI_API_KEY me rakhi hai)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # 2nd key (nano / dusra Gemini project)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
