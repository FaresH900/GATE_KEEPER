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

    # Create formatters
    # Detailed formatter for file
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Simplified formatter for console
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Create and configure file handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)

    # Create and configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    # Get the logger
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)

    # Remove any existing handlers to avoid duplicates
    logger.handlers = []

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Ensure propagation is enabled
    logger.propagate = True

    return logger

def create_app():
    # Setup logging
    logger = setup_logging()
    logger.info("Starting application initialization...")
    
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

        logger.info("Application startup completed successfully")

    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}")
        raise

    @app.before_request
    def log_request_info():
        # Don't log health check requests
        if request.path != '/health':
            logger.info(f"Received {request.method} request to {request.path}")
            
            # Log only essential headers
            important_headers = {
                'User-Agent': request.headers.get('User-Agent'),
                'Content-Type': request.headers.get('Content-Type')
            }
            logger.info(f"Important Headers: {important_headers}")
            
            # For file uploads, just log the file name, not the content
            if request.files:
                files_info = {key: value.filename for key, value in request.files.items()}
                logger.info(f"Uploaded files: {files_info}")
            elif request.method != 'GET' and not request.files:
                # For non-GET requests without files, log only the first 100 characters of the body
                body = request.get_data(as_text=True)
                if len(body) > 100:
                    body = body[:100] + "..."
                logger.info(f"Request body preview: {body}")

    @app.after_request
    def log_response_info(response):
        if request.path != '/health':
            logger.info(f"Response status: {response.status}")
            
            # Log response size instead of content
            response_size = len(response.get_data())
            logger.info(f"Response size: {response_size} bytes")
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return {"error": "Internal server error"}, 500

    return app