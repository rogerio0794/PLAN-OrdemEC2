from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    CORS(app)

    from app.routes.optimizer_routes import optimizer_bp
    app.register_blueprint(optimizer_bp)

    return app