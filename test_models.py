# import google.generativeai as genai
# from app.config.settings import Config

# genai.configure(api_key=Config.OPENAI_API_KEY)  # same as in ChatEngine

# print("Listing models...")
# for m in genai.list_models():
#     print(m.name, "->", m.supported_generation_methods)


# import requests
# from app.config.settings import Config


# def test_deapi_key():
#     """
#     Simple sanity check:
#     1) .env se de_api_key load ho rahi hai ya nahi
#     2) deAPI txt2img endpoint 200 de raha hai ya 401/403 etc
#     """

#     api_key = Config.DEAPI_KEY
#     print("DEAPI_KEY from Config:", "LOADED" if api_key else " MISSING")

#     if not api_key:
#         print("ERROR: de_api_key env var missing. Check your .env file.")
#         return

#     headers = {
#         "Authorization": f"Bearer {api_key}",
#         "Accept": "application/json",
#         "Content-Type": "application/json",
#     }

#     payload = {
#         "prompt": "a cute test cat image, simple flat illustration",
#         "negative_prompt": "blurry, low quality",
#         "model": "Flux1schnell",  # deAPI docs example model
#         "loras": [],
#         "width": 512,
#         "height": 512,
#         "guidance": 7.5,
#         "steps": 10,
#         "seed": 12345,
#     }

#     print("\n→ Calling deAPI txt2img...")
#     try:
#         resp = requests.post(
#             "https://api.deapi.ai/api/v1/client/txt2img",
#             json=payload,
#             headers=headers,
#             timeout=60,
#         )
#         print("HTTP status:", resp.status_code)
#         print("Raw response text:", resp.text[:500], "...\n")  # first 500 chars

#         # Agar yaha error mila to raise_for_status ka message clearly dikhega
#         resp.raise_for_status()
#         data = resp.json()
#         print("Parsed JSON:", data)

#         request_id = data.get("data", {}).get("request_id")
#         if request_id:
#             print("\nKey WORKING. Got request_id:", request_id)
#         else:
#             print("\n200 status mila but request_id missing – payload ya plan check karo.")

#     except requests.exceptions.HTTPError as e:
#         print("\nHTTPError from deAPI:", e)
#     except Exception as e:
#         print("\nOther error while calling deAPI:", repr(e))


# if __name__ == "__main__":
#     test_deapi_key()


# api key se model ko fetch karwaya hai 
import requests
from app.config.settings import Config

headers = {
    "Authorization": f"Bearer {Config.DEAPI_KEY}",
    "Accept": "application/json",
}

resp = requests.get(
    "https://api.deapi.ai/api/v1/client/models",
    headers=headers,
    timeout=30,
)

print(resp.status_code)
print(resp.text)
