import os
from dotenv import load_dotenv

# variable load karne ke liye 
load_dotenv()

class Config:
    # first google api key
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # first rply ke liye dusri key 
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # deapi key for image generation
    DEAPI_KEY = os.getenv("de_api_key")

    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
