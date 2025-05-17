from flask import Blueprint, jsonify
import os, json
from config import DATA_PATH

kb_blueprint = Blueprint("kb", __name__)

@kb_blueprint.route("/kb/<location>", methods=["GET"])
def get_kb(location):
    try:
        with open(os.path.join(DATA_PATH, f"{location}.json")) as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({"error": "Knowledge not found"}), 404
