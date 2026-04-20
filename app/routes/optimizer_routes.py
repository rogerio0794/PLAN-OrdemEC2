# app/routes/optimizer_routes.py

from flask import Blueprint, request, jsonify
from app.services.optimizer_service import run_optimization
from app.utils.validators import validate_request

optimizer_bp = Blueprint("optimizer", __name__)


@optimizer_bp.route("/otimizar", methods=["POST"])
def otimizar():
    data = request.get_json()

    is_valid, error = validate_request(data)
    if not is_valid:
        return jsonify({"error": error}), 400

    try:
        result = run_optimization(data)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "error": "Erro interno",
            "details": str(e)
        }), 500