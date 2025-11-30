import google.generativeai as genai
from app.config.settings import Config


class ChatEngine:
    def __init__(self, source: str = "openai", mode: str = "chat"):
        """
        source:
            "openai" -> uses Config.OPENAI_API_KEY  (tumhari pehli key)
            "gemini" -> uses Config.GEMINI_API_KEY  (dusri key / nano wali)
        
        mode:
            "chat" -> normal chatting model
            "nano" -> nano / lightweight model (agar tumne AI Studio me koi nano-type model banaya ho)
        """

        # --- Select API key based on source ---
        if source == "gemini":
            api_key = Config.GEMINI_API_KEY
        else:
            api_key = Config.OPENAI_API_KEY

        if not api_key:
            raise ValueError("API key missing. Check your .env and Config settings.")

        genai.configure(api_key=api_key)

        # --- Select model name based on mode ---
        if mode == "nano":
            # yahan tum apna nano model ka exact naam daal sakta hai
            # e.g. "models/gemini-1.5-flash-8b" ya jo AI Studio me show ho
            model_name = "gemini-1.5-flash-8b"
        else:
            # normal chat model
            model_name = "gemini-flash-latest"

        self.model = genai.GenerativeModel(model_name)

        # OpenAI-style internal message history
        self.messages = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]

    def _to_gemini_history(self):
        """
        Convert OpenAI-style messages to Gemini format:
        OpenAI roles: system / user / assistant
        Gemini roles: user / model
        """
        history = []
        for m in self.messages:
            if m["role"] == "assistant":
                role = "model"
            else:  # user ya system dono ko "user" treat kar rahe
                role = "user"

            history.append({
                "role": role,
                "parts": [m["content"]],
            })
        return history

    def get_response(self, user_input: str) -> str:
        # Add the user's message to conversation history
        self.messages.append({"role": "user", "content": user_input})

        # Build Gemini-compatible history
        history = self._to_gemini_history()

        # IMPORTANT: use contents=history
        response = self.model.generate_content(contents=history)

        # Extract text response
        reply = response.text or ""
        # Save assistant reply for future context
        self.messages.append({"role": "assistant", "content": reply})
        return reply
