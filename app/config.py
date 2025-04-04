# app/config.py
import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:@localhost/facial_recognition'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Models directory
    MODELS_DIR = os.path.join(BASE_DIR, 'models')
    YOLO_MODEL_PATH = os.path.join(MODELS_DIR, 'yolo11m_car_plate_trained.pt')
    
    # Instance directory for variable data
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    UPLOAD_FOLDER = os.path.join(INSTANCE_DIR, 'uploads')
    DEBUG_DIR = os.path.join(INSTANCE_DIR, 'debug')
    
    # Logs directory
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    YOLO_CONF_THRESHOLD = 0.25
    OCR_CONF_THRESHOLD = 0.7