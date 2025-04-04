from flask import Flask, request
import os
import logging
from datetime import datetime
from app.routes.api import api
from app.config import Config
from app.extensions import db

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
    app.config.from_object(Config)

    try:
        # Initialize extensions
        logger.info("Initializing database...")
        db.init_app(app)

        # Ensure required directories exist
        logger.info("Creating required directories...")
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.DEBUG_DIR, exist_ok=True)

        # Create database tables
        logger.info("Creating database tables...")
        with app.app_context():
            db.create_all()

        # Register blueprints
        logger.info("Registering blueprints...")
        app.register_blueprint(api, url_prefix='/api')

        # Add root route
        @app.route('/')
        def home():
            return {
                'status': 'online',
                'version': '1.0',
                'endpoints': {
                    'add_guest': '/api/add_guest',
                    'validate_face': '/api/validate_face',
                    'recognize_plate': '/api/recognize'
                }
            }

        # Add error handlers
        @app.errorhandler(404)
        def not_found_error(error):
            logger.info(f"404 Error: {request.url}")
            return {
                'error': 'Not Found',
                'message': 'The requested URL was not found on the server.',
                'available_endpoints': {
                    'add_guest': '/api/add_guest',
                    'validate_face': '/api/validate_face',
                    'recognize_plate': '/api/recognize'
                }
            }, 404

        @app.errorhandler(500)
        def internal_error(error):
            logger.error(f"500 Error: {str(error)}")
            return {'error': 'Internal Server Error'}, 500

        @app.before_request
        def log_request_info():
            if not request.path.startswith('/static'):  # Skip logging static file requests
                logger.info(f"Received {request.method} request to {request.path}")
                important_headers = {
                    'User-Agent': request.headers.get('User-Agent'),
                    'Content-Type': request.headers.get('Content-Type')
                }
                logger.info(f"Important Headers: {important_headers}")

        @app.after_request
        def log_response_info(response):
            logger.info(f"Response status: {response.status}")
            logger.info(f"Response size: {len(response.get_data())} bytes")
            return response

        logger.info("Application startup completed successfully")

    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}")
        raise

    return app