from flask import (
    Flask, 
    request, 
    jsonify,
    render_template,
    redirect,
    url_for
)
from flask_jwt_extended import (
    JWTManager, 
    jwt_required, 
    get_jwt_identity, 
    verify_jwt_in_request
)
from flask_cors import CORS
import os
import logging
from datetime import datetime, timezone
from app.config import Config
from app.extensions import db, bcrypt
from app.routes.auth import auth_bp
from app.routes.api import api_bp
from app.routes.admin import admin_bp
from app.routes.resident import resident_bp
from app.models.token import TokenBlocklist  # Add this import
from app.models.user import User, UserRole

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

def create_app():
    # Setup logging
    logger = setup_logging()
    
    # Create Flask app
    app = Flask(__name__)
    CORS(app, resources={
        r"/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"],
            "supports_credentials": True
        }
    })
    app.config.from_object(Config)

    try:
        # Initialize extensions
        logger.info("Initializing database...")
        db.init_app(app)
        bcrypt.init_app(app)
        jwt = JWTManager(app)

        # Ensure required directories exist
        logger.info("Creating required directories...")
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.DEBUG_DIR, exist_ok=True)

        # Create database tables
        logger.info("Creating database tables...")
        with app.app_context():
            db.create_all()

        # JWT configuration
        @jwt.token_in_blocklist_loader
        def check_if_token_revoked(jwt_header, jwt_payload):
            jti = jwt_payload["jti"]
            token = TokenBlocklist.query.filter_by(jti=jti).first()
            return token is not None

        @jwt.expired_token_loader
        def expired_token_callback(jwt_header, jwt_payload):
            return jsonify({
                'status': 401,
                'sub_status': 42,
                'msg': 'The token has expired'
            }), 401

        @jwt.invalid_token_loader
        def invalid_token_callback(error):
            return jsonify({
                'status': 401,
                'sub_status': 43,
                'msg': 'Invalid token'
            }), 401

        @jwt.unauthorized_loader
        def missing_token_callback(error):
            return jsonify({
                'status': 401,
                'sub_status': 44,
                'msg': 'Request does not contain a valid token'
            }), 401

        @jwt.revoked_token_loader
        def revoked_token_callback(jwt_header, jwt_payload):
            return jsonify({
                'status': 401,
                'sub_status': 45,
                'msg': 'The token has been revoked'
            }), 401

        # Register blueprints
        logger.info("Registering blueprints...")
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(resident_bp, url_prefix='/resident')

        # Add root route
        @app.route('/')
        def home():
            try:
                # Try to verify JWT token
                verify_jwt_in_request(optional=True)
                current_user_id = get_jwt_identity()
                if current_user_id:
                    # Get user from database
                    user = User.query.get(int(current_user_id))
                    if user:
                        # Redirect based on role
                        if user.role == 'ADMIN':
                            return redirect(url_for('admin.dashboard'))
                        elif user.role == 'RESIDENT':
                            return redirect(url_for('resident.dashboard'))
                        elif user.role == 'GATEKEEPER':
                            return redirect(url_for('gatekeeper.dashboard'))

                # If no valid token or user not found, show login page
                return render_template('auth/login.html')
            except:
                # If any error occurs, show login page
                return render_template('auth/login.html')

        # Add dashboard routes for each role
        @app.route('/admin/dashboard')
        @jwt_required()
        def admin_dashboard():
            current_user = User.query.get(int(get_jwt_identity()))
            if not current_user or current_user.role != 'ADMIN':
                return redirect(url_for('home'))
            return render_template('admin/dashboard.html')

        @app.route('/resident/dashboard')
        @jwt_required()
        def resident_dashboard():
            current_user = User.query.get(int(get_jwt_identity()))
            if not current_user or current_user.role != 'RESIDENT':
                return redirect(url_for('home'))
            return render_template('resident/dashboard.html')

        @app.route('/gatekeeper/dashboard')
        @jwt_required()
        def gatekeeper_dashboard():
            current_user = User.query.get(int(get_jwt_identity()))
            if not current_user or current_user.role != 'GATEKEEPER':
                return redirect(url_for('home'))
            return render_template('gatekeeper/dashboard.html')

        # Add health check endpoint
        @app.route('/health')
        def health_check():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'database': 'connected' if db.engine.pool.checkedout() == 0 else 'busy'
            })

        # app/__init__.py
        @app.errorhandler(Exception)
        def handle_error(error):
            if isinstance(error, HTTPException):
                return jsonify({
                    "error": error.name,
                    "message": error.description
                }), error.code
            
            app.logger.error(f"Unexpected error: {str(error)}")
            return jsonify({
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }), 500

        
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
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            if request.path != '/health':
                logger.info(f"Response status: {response.status}")
                logger.info(f"Response size: {len(response.get_data())} bytes")
            return response

        logger.info("Application startup completed successfully")

    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}")
        raise

    return app