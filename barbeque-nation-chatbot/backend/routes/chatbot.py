from flask import Blueprint, request, jsonify

chatbot_blueprint = Blueprint("chatbot", __name__)

@chatbot_blueprint.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message")
    return jsonify({"response": f"You said: {user_input}"})
