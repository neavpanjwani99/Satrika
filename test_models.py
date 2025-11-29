import google.generativeai as genai
from app.config.settings import Config

genai.configure(api_key=Config.OPENAI_API_KEY)  # same as in ChatEngine

print("Listing models...")
for m in genai.list_models():
    print(m.name, "->", m.supported_generation_methods)
