from flask import Blueprint, render_template, request, jsonify
from app.logic.chat_engine import ChatEngine
from app.logic.history_manager import HistoryManager
from app.logic.image_engine import ImageEngine

main_bp = Blueprint("main", __name__)
chat_engine_normal = ChatEngine(source="openai", mode="chat")
chat_engine_nano = ChatEngine(source="gemini", mode="nano")
image_engine = ImageEngine()
history = HistoryManager()

@main_bp.route("/")
def home():
    return render_template("index.html")

@main_bp.route("/new_chat", methods=["POST"])
#exception handling 
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
        engine_type = data.get("engine", "normal") #option selection 

        if not session_id or not user_input:
            return jsonify({"error": "Missing session_id or message"}), 400

        if engine_type == "nano":
            engine = chat_engine_nano
        else:
            engine = chat_engine_normal
        bot_response = engine.get_response(user_input)
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

@main_bp.route("/generate_image", methods=["post"])
def generate_image():
    try:
        data=request.json or {}
        session_id=data.get("session_id")
        prompt=data.get("prompt")
        negative_prompt=data.get("negative_prompt","")
        
        if not prompt:
            return jsonify({
                "error" : "give some command(Prompt) "
            }),400
            
        result = image_engine.generate_image(prompt=prompt, negative_prompt=negative_prompt,)
        if session_id:
            history.save_message(session_id, "user", f"[IMAGE PROMPT] {prompt}")
            history.save_message(
                session_id,
                "bot",
                f"[IMAGE GENERATED] {result.get('image_url')}",
            )

        return jsonify({
            "request_id": result["request_id"],
            "status": result["status"],
            "image_url": result["image_url"],
            "preview_url": result.get("preview_url"),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500