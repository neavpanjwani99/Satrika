import google.generativeai as genai
from app.config.settings import Config


class ChatEngine:
    def __init__(self):
        # Configure with your Google AI Studio API key
        genai.configure(api_key=Config.OPENAI_API_KEY)  # or Config.GEMINI_API_KEY

        # Use a model that works with v1beta
        # If your SDK is older, "gemini-pro" is the safe choice.
        self.model = genai.GenerativeModel("gemini-flash-latest")
        
        # Keep OpenAI-style internal message history
        self.messages = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]

    def _to_gemini_history(self):
        """
        Convert OpenAI-style messages to Gemini format:
        - OpenAI roles: system / user / assistant
        - Gemini roles: user / model
        """
        history = []
        for m in self.messages:
            if m["role"] == "user":
                role = "user"
            elif m["role"] == "assistant":
                role = "model"
            else:  # "system" or anything else
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

        # IMPORTANT: use contents=history, not just history
        response = self.model.generate_content(contents=history)

        # Extract text response
        reply = response.text or ""
        # Save assistant reply for future context
        self.messages.append({"role": "assistant", "content": reply})
        return reply
