from flask import Blueprint, render_template, request, jsonify
from app.logic.chat_engine import ChatEngine
from app.logic.history_manager import HistoryManager

main_bp = Blueprint("main", __name__)

# 🔹 Normal chat (pehli key, normal model)
chat_engine_normal = ChatEngine(source="openai", mode="chat")

# 🔹 Nano chat (dusri key, nano / lightweight model)
chat_engine_nano = ChatEngine(source="gemini", mode="nano")

# In-memory chat history
history = HistoryManager()


@main_bp.route("/")
def home():
    return render_template("index.html")


@main_bp.route("/new_chat", methods=["POST"])
def new_chat():
    try:
        chat = history.create_new_chat()
        return jsonify(chat)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_bp.route("/list_chats", methods=["GET"])
def list_chats():
    try:
        chats = history.get_all_chats()
        return jsonify(chats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_bp.route("/load_chat/<session_id>", methods=["GET"])
def load_chat(session_id):
    try:
        chat = history.get_chat(session_id)
        if chat:
            return jsonify(chat)
        else:
            return jsonify({"error": "Chat not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json or {}
        session_id = data.get("session_id")
        user_input = data.get("message")

        # optional: "engine": "normal" / "nano"
        engine_type = data.get("engine", "normal")

        if not session_id or not user_input:
            return jsonify({"error": "Missing session_id or message"}), 400

        # 🔹 Select which engine to use
        if engine_type == "nano":
            engine = chat_engine_nano
        else:
            engine = chat_engine_normal

        # Get AI response
        bot_response = engine.get_response(user_input)

        # Save messages to history
        history.save_message(session_id, "user", user_input)
        history.save_message(session_id, "bot", bot_response)

        return jsonify({"reply": bot_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_bp.route("/delete_chat/<session_id>", methods=["DELETE"])
def delete_chat(session_id):
    try:
        success = history.delete_chat(session_id)
        if success:
            return jsonify({"status": "success"})
        else:
            return jsonify(
                {"status": "error", "message": "Chat not found"}
            ), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_bp.route("/update_chat/<session_id>", methods=["PUT"])
def update_chat(session_id):
    try:
        data = request.json or {}
        new_title = data.get("title")

        if not new_title:
            return jsonify({"error": "Title is required"}), 400

        success = history.update_chat_title(session_id, new_title)
        if success:
            return jsonify({"status": "success"})
        else:
            return jsonify(
                {"status": "error", "message": "Chat not found"}
            ), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
