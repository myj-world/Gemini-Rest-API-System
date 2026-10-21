from flask import Blueprint, jsonify, request

from app.services.gemini import get_gemini_client

bp = Blueprint("generate", __name__, url_prefix="/api")


@bp.post("/generate")
def generate():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    prompt = body.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        return jsonify({"error": "prompt must be a non-empty string"}), 400

    response_format = body.get("response_format", "text")
    if response_format not in ("text", "json"):
        return jsonify({"error": "response_format must be 'text' or 'json'"}), 400

    response = get_gemini_client().generate(prompt.strip(), response_format)
    return jsonify({"response_format": response_format, "response": response})
