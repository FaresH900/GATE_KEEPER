from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import logging
from app.config import Config
from app.extensions import db, bcrypt
from app.routes import auth_bp, admin_bp, api_bp, resident_bp
from app.models.facial_recognition import FacialRecognition
from app.models.license_plate_recognizer import LicensePlateRecognizer

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    CORS(app, resources={r"/*": {"origins": ["*"]}})
    db.init_app(app)
    bcrypt.init_app(app)
    jwt = JWTManager(app)

    # Initialize global models
    with app.app_context():
        app.facial_recognition = FacialRecognition()
        app.recognizer = LicensePlateRecognizer(Config.YOLO_MODEL_PATH, Config.DEBUG_DIR)
        logger.info("FacialRecognition and LicensePlateRecognizer models loaded globally.")

    # Register blueprints
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
        return jsonify({'message': 'Token has expired', 'error': 'token_expired'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'message': 'Invalid token', 'error': 'invalid_token'}), 401

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({'message': 'Missing or invalid token', 'error': 'unauthorized'}), 401

    return app