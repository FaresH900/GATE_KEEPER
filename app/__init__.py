from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from datetime import datetime,timezone
import logging
from app.config import Config
from app.extensions import db, bcrypt
from app.routes.auth import auth_bp
# from app.routes import auth_bp, admin_bp, api_bp, resident_bp
from app.routes.api import api_bp
from app.routes.admin import admin_bp
from app.routes.resident import resident_bp
from app.models.facial_recognition import FacialRecognition
from app.models.license_plate_recognizer import LicensePlateRecognizer



def setup_logging():
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Create a log filename with timestamp
    log_filename = os.path.join(logs_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')

    # Configure logging
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Create file handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Get the logger
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)

    # Remove any existing handlers
    if logger.handlers:
        logger.handlers.clear()

    # Add the handler
    logger.addHandler(file_handler)

    # Disable propagation to prevent duplicate logs
    logger.propagate = False

    return logger


# Initialize logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

def create_app():

    logger = setup_logging()

    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    CORS(app, resources={r"/*": {"origins": ["*"], "supports_credentials": True}})    
    logger.info("Intializing database...")
    db.init_app(app)
    bcrypt.init_app(app)
    jwt = JWTManager(app)

    # Ensure required directories exist
    logger.info("Creating required directories...")
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.DEBUG_DIR, exist_ok=True)

    # Initialize global models
    with app.app_context():
        app.facial_recognition = FacialRecognition()
        app.recognizer = LicensePlateRecognizer(Config.YOLO_MODEL_PATH, Config.DEBUG_DIR)
        logger.info("FacialRecognition and LicensePlateRecognizer models loaded globally.")
        logger.info("Creating database tables...")
        db.create_all()

    # Register blueprints
    logger.info("Registering blueprints...")
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(resident_bp, url_prefix='/resident')

    # Routes
    @app.route('/')
    def home():
        try:
            from flask_jwt_extended import current_user
            if not current_user:
                return render_template('auth/login.html')
            return redirect(url_for(f'{current_user.role.lower()}_bp.dashboard'))
        except Exception as e:
            logger.error(f"Error in home route: {str(e)}")
            return render_template('auth/login.html')

    @app.route('/health')
    def health_check():
        db_status = "connected" if db.engine.pool.checkedout() else "disconnected"
        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'timestamp': datetime.now().isoformat()
        })

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logger.info(f"jwt.expired_token_loader jwt_header:{jwt_header} jwt_payload:{jwt_payload}")
        return jsonify({'message': 'Token has expired', 'error': 'token_expired'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        logger.info(f"jwt.invalid_token_loader error:{error}")
        return jsonify({'message': 'Invalid token', 'error': 'invalid_token'}), 401

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        logger.info(f"jwt.unauthorized_loader error:{error}")
        return jsonify({'message': 'Missing or invalid token', 'error': 'unauthorized'}), 401


    @app.before_request
    def log_request_info():
        if not request.path.startswith('/static') and request.path != '/health':
            logger.info(f"Received {request.method} request to {request.path}")
            important_headers = {
                'User-Agent': request.headers.get('User-Agent'),
                'Content-Type': request.headers.get('Content-Type')
            }
            logger.info(f"Important Headers: {important_headers}")

    @app.after_request
    def log_response_info(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-CSRF-TOKEN')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        if request.path != '/health':
            logger.info(f"Response status: {response.status}")
            logger.info(f"Response size: {len(response.get_data())} bytes")
        return response

    logger.info("Application startup completed successfully")
    return app