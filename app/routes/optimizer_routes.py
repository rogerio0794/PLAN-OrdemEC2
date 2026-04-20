# app/routes/optimizer_routes.py

from flask import Blueprint, request, jsonify
from app.services.optimizer_service import run_optimization
from app.utils.validators import validate_request
import os
import threading  # <-- Necessário para rodar em segundo plano
from utils.io import *

optimizer_bp = Blueprint("optimizer", __name__)

# Nome do arquivo de controle
RESULT_FILE = "saida_completa.json"

@optimizer_bp.route("/status", methods=["GET"])
def check_status():    
    if os.path.exists("saida_completa.json"):
        dados = abrir_json("saida_completa.json")
        return jsonify({"status": "ready", "data": dados}), 200
    else:
        return jsonify({"status": "processing"}), 200


@optimizer_bp.route("/otimizar", methods=["POST"])
def otimizar():
    # 1. Limpa o resultado anterior se ele existir
    if os.path.exists(RESULT_FILE):
        os.remove(RESULT_FILE)
    
    print(">>> RECEBI UMA REQUISIÇÃO NA ROTA OTIMIZAR! <<<", flush=True)
    data = request.get_json()    

    # 2. Validação básica
    is_valid, error = validate_request(data)
    if not is_valid:
        return jsonify({"error": error}), 400

    try:
        # 3. DISPARA O CÁLCULO EM SEGUNDO PLANO (THREAD)
        # O Flask não vai esperar o run_optimization terminar
        thread = threading.Thread(target=run_optimization, args=(data,))
        thread.start()

        # 4. RESPONDE IMEDIATAMENTE AO FRONT-END
        # Usamos o código 202 (Accepted) que indica que o trabalho começou mas não terminou
        return jsonify({
            "message": "Otimização iniciada com sucesso",
            "status": "processing"
        }), 202

    except Exception as e:
        print(f"Erro ao disparar thread: {e}")
        return jsonify({
            "error": "Erro ao iniciar processamento",
            "details": str(e)
        }), 500