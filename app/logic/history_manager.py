import uuid
from datetime import datetime


class HistoryManager:
    def __init__(self):
        # Simple in-memory store
        # TODO: chahe to baad me ise DB / JSON file se replace kar sakta hai
        self.chats = {}  # {chat_id: chat_data}

    def _now(self):
        return datetime.utcnow().isoformat()

    def create_new_chat(self):
        chat_id = str(uuid.uuid4())
        chat = {
            "id": chat_id,
            "title": "New Chat",
            "created_at": self._now(),
            "updated_at": self._now(),
            "messages": []  # list of {sender, message, timestamp}
        }
        self.chats[chat_id] = chat
        return chat

    def get_all_chats(self):
        """
        Sidebar ke liye sirf summary list:
        id, title, created_at, updated_at
        """
        chats = []
        for chat in self.chats.values():
            chats.append({
                "id": chat["id"],
                "title": chat["title"],
                "created_at": chat.get("created_at"),
                "updated_at": chat.get("updated_at"),
            })
        return chats

    def get_chat(self, chat_id):
        """
        Ek chat + uske saare messages
        """
        chat = self.chats.get(chat_id)
        if not chat:
            return None
        return chat

    def save_message(self, chat_id, sender, message):
        chat = self.chats.get(chat_id)
        if not chat:
            return False

        msg = {
            "sender": sender,      # "user" or "bot"
            "message": message,
            "timestamp": self._now()
        }
        chat["messages"].append(msg)
        chat["updated_at"] = self._now()

        # Optional: first user message se title set karo
        if sender == "user" and chat["title"] == "New Chat":
            chat["title"] = message[:40]

        return True

    def delete_chat(self, chat_id):
        if chat_id in self.chats:
            del self.chats[chat_id]
            return True
        return False

    def update_chat_title(self, chat_id, new_title):
        chat = self.chats.get(chat_id)
        if not chat:
            return False
        chat["title"] = new_title
        chat["updated_at"] = self._now()
        return True
