import os

from flask import Flask, jsonify, render_template, send_from_directory
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException

from app.routes.generate import bp as generate_bp
from app.routes.health import bp as health_bp
from app.services.gemini import GeminiError


def create_app():
    load_dotenv()
    app = Flask(__name__, static_folder="static", template_folder="templates")

    app.register_blueprint(generate_bp)
    app.register_blueprint(health_bp)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/icon.png")
    def icon():
        return send_from_directory(
            os.path.dirname(app.root_path), "icon.png", mimetype="image/png"
        )

    @app.errorhandler(GeminiError)
    def handle_gemini_error(error):
        app.logger.error("Gemini API request failed: %s", error)
        return jsonify({"error": str(error)}), 503

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        if isinstance(error, HTTPException):
            return jsonify({"error": error.description}), error.code
        app.logger.exception("Unhandled error")
        return jsonify({"error": "Internal server error"}), 500

    return app
