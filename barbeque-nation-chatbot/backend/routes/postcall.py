from flask import Blueprint, request, jsonify

postcall_blueprint = Blueprint("postcall", __name__)

@postcall_blueprint.route("/postcall", methods=["POST"])
def postcall():
    data = request.json
    return jsonify({"status": "Post-call analysis captured"})
