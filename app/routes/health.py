from flask import Blueprint, jsonify
import os

bp = Blueprint("health", __name__)


@bp.route("/api/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "service": "Gemini REST API System",
            "gemini_api_key_configured": bool(os.getenv("GEMINI_API_KEY")),
        }
    )
