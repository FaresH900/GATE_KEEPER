app/
├── config.py
├── extensions.py
├── __init__.py
├── models
│   ├── facial_recognition.py
│   ├── guest.py
│   ├── __init__.py
│   ├── license_plate_recognizer_old.py
│   ├── license_plate_recognizer.py
│   ├── __pycache__
│   │   ├── facial_recognition.cpython-311.pyc
│   │   ├── guest.cpython-311.pyc
│   │   ├── __init__.cpython-311.pyc
│   │   ├── license_plate_recognizer.cpython-311.pyc
│   │   ├── token.cpython-311.pyc
│   │   └── user.cpython-311.pyc
│   ├── token.py
│   └── user.py
├── __pycache__
│   ├── config.cpython-311.pyc
│   ├── extensions.cpython-311.pyc
│   └── __init__.cpython-311.pyc
├── routes
│   ├── admin.py
│   ├── api.py
│   ├── auth.py
│   ├── gatekeeper.py
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── admin.cpython-311.pyc
│   │   ├── api.cpython-311.pyc
│   │   ├── auth.cpython-311.pyc
│   │   ├── gatekeeper.cpython-311.pyc
│   │   ├── __init__.cpython-311.pyc
│   │   └── resident.cpython-311.pyc
│   └── resident.py
├── static
│   ├── debug
│   │   ├── debug_20250406_232235.jpg
│   │   ├── debug_20250406_233555.jpg
│   │   ├── debug_20250406_234054.jpg
│   │   ├── debug_20250406_234507.jpg
│   │   ├── debug_20250406_235244.jpg
│   │   ├── debug_20250406_235337.jpg
│   │   ├── debug_20250407_000142.jpg
│   │   ├── debug_20250407_000408.jpg
│   │   ├── debug_20250407_001133.jpg
│   │   ├── debug_20250407_002836.jpg
│   │   ├── debug_20250407_002921.jpg
│   │   ├── debug_20250407_003226.jpg
│   │   ├── debug_20250407_003305.jpg
│   │   ├── debug_20250407_003401.jpg
│   │   ├── debug_20250407_003511.jpg
│   │   ├── debug_20250407_003617.jpg
│   │   ├── debug_20250407_003822.jpg
│   │   ├── debug_20250407_003844.jpg
│   │   ├── debug_20250407_010001.jpg
│   │   ├── debug_20250407_010003.jpg
│   │   ├── debug_20250407_010153.jpg
│   │   ├── debug_20250407_010217.jpg
│   │   ├── debug_20250407_011616.jpg
│   │   ├── debug_20250407_011638.jpg
│   │   ├── debug_20250407_085842.jpg
│   │   ├── debug_20250407_085858.jpg
│   │   ├── debug_20250408_104551.jpg
│   │   ├── debug_20250408_130314.jpg
│   │   ├── debug_20250408_130653.jpg
│   │   ├── debug_20250408_131043.jpg
│   │   ├── debug_20250408_131505.jpg
│   │   ├── debug_20250408_134603.jpg
│   │   ├── debug_20250408_134943.jpg
│   │   ├── debug_20250408_153942.jpg
│   │   ├── debug_20250408_154048.jpg
│   │   ├── debug_20250408_155356.jpg
│   │   ├── debug_20250408_155430.jpg
│   │   ├── debug_20250408_180308.jpg
│   │   ├── debug_20250408_182444.jpg
│   │   ├── debug_20250408_192626.jpg
│   │   ├── debug_20250408_192836.jpg
│   │   ├── debug_20250409_030749.jpg
│   │   ├── debug_20250409_031024.jpg
│   │   └── debug_20250409_031407.jpg
│   └── uploads
├── templates
│   ├── admin
│   │   └── dashboard.html
│   ├── auth
│   │   └── login.html
│   ├── base.html
│   ├── gatekeeper
│   │   └── dashboard.html
│   └── resident
│       └── dashboard.html
├── utils
│   ├── auth.py
│   ├── helpers.py
│   ├── __init__.py
│   └── __pycache__
│       ├── helpers.cpython-311.pyc
│       └── __init__.cpython-311.pyc
└── run.py
16 directories, 86 files

=== File: run.py ===
======================================================================
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
======================================================================
=== File: config.py ===
======================================================================
import os
from datetime import timedelta  

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:@localhost/gatekeeping_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Models directory
    MODELS_DIR = os.path.join(BASE_DIR, 'models')
    YOLO_MODEL_PATH = os.path.join(MODELS_DIR, 'yolo11m_car_plate_trained.pt')
    
    # Static folder for debug images
    STATIC_DIR = os.path.join(BASE_DIR, 'app', 'static')  # app/static/
    DEBUG_DIR = os.path.join(STATIC_DIR, 'debug')         # app/static/debug/
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'instance', 'uploads')  # Keep uploads separate

    # Logs directory
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    YOLO_CONF_THRESHOLD = 0.25
    OCR_CONF_THRESHOLD = 0.7

    # JWT Configuration
    # python -c "import secrets;k=secrets.token_hex(16);print(k)"
    JWT_SECRET_KEY = '31e39bcb51dd6b40439b8519eba7dd85'  # Change this in production
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    JWT_TOKEN_LOCATION = ['cookies']  # Look for token in cookies
    JWT_COOKIE_SECURE = True  # Set to True in production with HTTPS
    JWT_COOKIE_SAMESITE = 'Lax'  # Prevents CSRF, allows redirects
    JWT_ACCESS_COOKIE_NAME = 'access_token_cookie'  # Cookie name
    JWT_COOKIE_CSRF_PROTECT = True  # Enable CSRF protection
    
    CORS_HEADERS = 'Content-Type'
    SECURITY_HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Credentials': 'true'
    }
======================================================================

=== File: extensions.py ===
======================================================================
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()
======================================================================

=== File: __init__.py ===
======================================================================
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
from app.routes.gatekeeper import gatekeeper_bp
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
    app.register_blueprint(gatekeeper_bp, url_prefix='/gatekeeper')

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
======================================================================

=== File: models/facial_recognition.py ===
======================================================================
import torch
import numpy as np
import cv2
from facenet_pytorch import MTCNN, InceptionResnetV1
import pickle
import base64
import re
from PIL import Image

class FacialRecognition:
    VERSION = "1.0.0"
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.mtcnn = MTCNN(image_size=160, margin=10, keep_all=False, device=self.device)
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)

    def process_image_data(self, image_data):
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            image_data = re.sub('^data:image/.+;base64,', '', image_data)
            image_data = base64.b64decode(image_data)
        
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img

    def generate_embedding(self, image_data):
        img = self.process_image_data(image_data)
        if img is None:
            raise ValueError("Invalid image data")

        face = self.mtcnn(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if face is None:
            raise ValueError("No face detected")

        face = face.unsqueeze(0).to(self.device)
        embedding = self.resnet(face).detach().cpu().numpy().flatten()
        return embedding

    def compare_embeddings(self, embedding1, embedding2):
        return np.linalg.norm(embedding1 - embedding2)
======================================================================

=== File: models/guest.py ===
======================================================================
from app.extensions import db
from datetime import datetime, timedelta
import pickle
import numpy as np
from enum import Enum
import base64  # Add this import for image encoding

class GuestStatus(Enum):
    PENDING = 'PENDING'
    ALLOWED = 'ALLOWED'

class GuestInvitation(db.Model):
    __tablename__ = 'guest_invitation'
    
    id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(GuestStatus), default=GuestStatus.PENDING, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'status': self.status.value,
            'created_at': self.created_at.isoformat()
        }

class Guest(db.Model):
    __tablename__ = 'guest'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    embedding = db.Column(db.LargeBinary, nullable=False)
    face_image = db.Column(db.LargeBinary, nullable=False)
    resident_id = db.Column(db.Integer, db.ForeignKey('residents.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    resident = db.relationship('Resident', backref=db.backref('guests', lazy=True))
    invitations = db.relationship('GuestInvitation', backref='guest', lazy=True, cascade='all, delete-orphan')
    history = db.relationship('GuestHistory', backref='guest', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        current_invitation = self.get_current_invitation()
        return {
            'id': self.id,
            'name': self.name,
            'face_image': base64.b64encode(self.face_image).decode('utf-8') if self.face_image else None,
            'created_at': self.created_at.isoformat(),
            'resident': self.resident.to_dict() if self.resident else None,
            'current_invitation': current_invitation.to_dict() if current_invitation else None,
            'all_invitations': [inv.to_dict() for inv in self.invitations],
            'history': [h.to_dict() for h in self.history]
        }

    @staticmethod
    def add_guest(name, embedding, face_image, resident_id, invitation_end_date=None):
        """
        Add a new guest with face embedding and image
        """
        try:
            # Check for existing face matches
            existing_guests = Guest.query.all()
            
            for guest in existing_guests:
                stored_embedding = pickle.loads(guest.embedding)
                distance = np.linalg.norm(embedding - stored_embedding)
                
                if distance < 0.8:  # Threshold for face matching
                    # Create new invitation for existing guest if needed
                    if invitation_end_date:
                        new_invitation = GuestInvitation(
                            guest_id=guest.id,
                            end_date=invitation_end_date,
                            status=GuestStatus.PENDING
                        )
                        db.session.add(new_invitation)
                        db.session.commit()
                        return {
                            'status': 'exists',
                            'message': 'New invitation created for existing guest',
                            'guest': guest,
                            'invitation': new_invitation
                        }
                    return {
                        'status': 'exists',
                        'message': 'Person already registered',
                        'guest': guest
                    }

            # Create new guest with face image
            new_guest = Guest(
                name=name,
                embedding=pickle.dumps(embedding),
                face_image=face_image,
                resident_id=resident_id
            )
            db.session.add(new_guest)
            db.session.flush()

            # Create invitation if end date provided
            if invitation_end_date:
                new_invitation = GuestInvitation(
                    guest_id=new_guest.id,
                    end_date=invitation_end_date,
                    status=GuestStatus.PENDING
                )
                db.session.add(new_invitation)
            
            db.session.commit()
            return {
                'status': 'new',
                'message': 'New guest registered successfully',
                'guest': new_guest
            }

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error adding guest: {str(e)}")

    def get_current_invitation(self):
        """Get the current valid invitation if any"""
        now = datetime.now()
        return GuestInvitation.query.filter(
            GuestInvitation.guest_id == self.id,
            GuestInvitation.start_date <= now,
            GuestInvitation.end_date >= now
        ).order_by(GuestInvitation.created_at.desc()).first()

    def update_invitation_status(self, invitation_id, new_status):
        """Update invitation status and create history entry"""
        invitation = GuestInvitation.query.get(invitation_id)
        if not invitation or invitation.guest_id != self.id:
            return False, "Invalid invitation"
        
        if invitation.status == new_status:
            return False, f"Invitation already {new_status.value}"
            
        invitation.status = new_status
        if new_status == GuestStatus.ALLOWED:
            history = GuestHistory(guest_id=self.id, invitation_id=invitation.id)
            db.session.add(history)
        db.session.commit()
        return True, "Status updated successfully"

class GuestHistory(db.Model):
    __tablename__ = 'guest_history'
    
    id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id', ondelete='CASCADE'), nullable=False)
    invitation_id = db.Column(db.Integer, db.ForeignKey('guest_invitation.id', ondelete='CASCADE'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'guest_id': self.guest_id,
            'invitation_id': self.invitation_id,
            'timestamp': self.timestamp.isoformat()
        }
======================================================================

=== File: models/__init__.py ===
======================================================================

======================================================================

=== File: models/license_plate_recognizer_old.py ===
======================================================================
from ultralytics import YOLO
from PIL import Image
from paddleocr import PaddleOCR
import cv2
import numpy as np
import os
from time import time
from datetime import datetime

class LicensePlateRecognizer:
    VERSION = "1.0.0"
    def __init__(self, model_path, debug_dir):
        self.model = YOLO(model_path)
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ar', 
                            det_db_box_thresh=0.7, 
                            det_db_unclip_ratio=1.7)
        self.debug_dir = debug_dir
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)  # Create app/static/debug/ if it doesn’t exist
    
    def save_debug_image(self, image, texts):
        filename = f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        debug_path = os.path.join(self.debug_dir, filename)
        cv2.imwrite(debug_path, image)
        return f"/static/debug/{filename}"  # Return URL path
    
    def crop_plate(self, img):
        # Perform prediction on the image
        results = self.model.predict(source=img, conf=0.25)

        # Open the image
        image = Image.open(img)

        for result in results:
            if result.boxes is not None and len(result.boxes) > 0:
                max_width = -1
                selected_box = None

                # Iterate through all detected boxes to find the one with the maximum width
                for box in result.boxes:
                    res = box.xyxy[0]  # Get the coordinates of the bounding box
                    width = res[2].item() - res[0].item()  # Calculate width (x_max - x_min)

                    if width > max_width:
                        max_width = width
                        selected_box = res  # Store the coordinates of the selected box

                if selected_box is not None:
                    x_min = selected_box[0].item()
                    y_min = selected_box[1].item()
                    x_max = selected_box[2].item()
                    y_max = selected_box[3].item()

                    # Crop the image using the bounding box coordinates
                    cropped_image = image.crop((x_min, y_min, x_max, y_max))
                    return cropped_image
            else:
                print("No bounding boxes detected.")
        return None

    def get_lower_box(self, results):
        if not results or not results[0]:
            return None, None, None
        if len(results[0]) == 1:
            bbox, (text, prob) = results[0][0]
            return text, prob, bbox
        # Multiple boxes: select the one with the highest bottom y-coordinate
        lower_box = max(results[0], key=lambda x: max([p[1] for p in x[0]]))  # Max y of bbox
        bbox, (text, prob) = lower_box
        return text, prob, bbox

    def detect_text(self, cropped_image):
        # Convert PIL Image to NumPy array first
        image_array = np.array(cropped_image)
        
        # Convert to BGR if the image has 3 channels (RGB)
        image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR) if len(image_array.shape) == 3 and image_array.shape[-1] == 3 else image_array

        # Split the image horizontally into two halves
        height, width = image.shape[:2]
        mid_point = width // 2
        left_half = image[:, :mid_point, :]  # Left half
        right_half = image[:, mid_point:, :]  # Right half

        # Perform OCR on each half and select the lower box
        detected_texts = []
        texts_only = []
        left_bbox = None
        right_bbox = None

        # OCR on left half
        left_results = self.ocr.ocr(left_half, cls=True)
        if left_results and left_results[0]:
            left_text, left_prob, left_bbox = self.get_lower_box(left_results)
            if left_text:
                detected_texts.append((left_text, left_prob))
                texts_only.append(left_text)

        # OCR on right half
        right_results = self.ocr.ocr(right_half, cls=True)
        if right_results and right_results[0]:
            right_text, right_prob, right_bbox = self.get_lower_box(right_results)
            if right_text:
                detected_texts.append((right_text, right_prob))
                texts_only.append(right_text)

        # Combine the halves back for visualization
        combined_image = np.hstack((left_half, right_half))

        # Draw bounding boxes on the combined image
        if left_bbox is not None:
            left_bbox = np.array(left_bbox).astype(int)
            cv2.polylines(combined_image, [left_bbox], isClosed=True, color=(0, 255, 0), thickness=1)
        if right_bbox is not None:
            right_bbox = np.array(right_bbox).astype(int)
            right_bbox[:, 0] += mid_point  # Shift x-coordinates to match combined image
            cv2.polylines(combined_image, [right_bbox], isClosed=True, color=(0, 255, 0), thickness=1)

        debug_url = self.save_debug_image(combined_image, detected_texts)
        return [detected_texts, texts_only, debug_url]
        
    @staticmethod
    def clean_text(texts):
        tmp = []
        for t in texts:
            t = t.replace(' ','')
            if not(ord(t[0]) >= 1569 and ord(t[0]) <= 1610):
                tmp.append(t[::-1])
            else:
                tmp.append(t)
        return tmp
======================================================================

=== File: models/license_plate_recognizer.py ===
======================================================================
from ultralytics import YOLO
from PIL import Image
from paddleocr import PaddleOCR
import cv2
import numpy as np
import os
from time import time
from datetime import datetime

class LicensePlateRecognizer:
    VERSION = "1.0.0"
    def __init__(self, model_path, debug_dir):
        self.model = YOLO(model_path)
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ar', 
                            det_db_box_thresh=0.7, 
                            det_db_unclip_ratio=1.7)
        self.debug_dir = debug_dir
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)  # Create app/static/debug/ if it doesn’t exist
    
    def save_debug_image(self, image, texts):
        filename = f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        debug_path = os.path.join(self.debug_dir, filename)
        cv2.imwrite(debug_path, image)
        return f"/static/debug/{filename}"  # Return URL path
    
    def crop_plate(self, img):
        # Perform prediction on the image
        results = self.model.predict(source=img, conf=0.25)

        # Open the image
        image = Image.open(img)

        for result in results:
            if result.boxes is not None and len(result.boxes) > 0:
                max_width = -1
                selected_box = None

                # Iterate through all detected boxes to find the one with the maximum width
                for box in result.boxes:
                    res = box.xyxy[0]  # Get the coordinates of the bounding box
                    width = res[2].item() - res[0].item()  # Calculate width (x_max - x_min)

                    if width > max_width:
                        max_width = width
                        selected_box = res  # Store the coordinates of the selected box

                if selected_box is not None:
                    x_min = selected_box[0].item()
                    y_min = selected_box[1].item()
                    x_max = selected_box[2].item()
                    y_max = selected_box[3].item()

                    # Crop the image using the bounding box coordinates
                    cropped_image = image.crop((x_min, y_min, x_max, y_max))
                    return cropped_image
            else:
                print("No bounding boxes detected.")
        return None

    def get_lower_box(self, results):
        if not results or not results[0]:
            return None, None, None
        if len(results[0]) == 1:
            bbox, (text, prob) = results[0][0]
            return text, prob, bbox
        # Multiple boxes: select the one with the highest bottom y-coordinate
        lower_box = max(results[0], key=lambda x: max([p[1] for p in x[0]]))  # Max y of bbox
        bbox, (text, prob) = lower_box
        return text, prob, bbox

    def detect_text(self, cropped_image):
        # Convert PIL Image to NumPy array first
        image_array = np.array(cropped_image)
        
        # Convert to BGR if the image has 3 channels (RGB)
        image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR) if len(image_array.shape) == 3 and image_array.shape[-1] == 3 else image_array

        # Split the image horizontally into two halves
        height, width = image.shape[:2]
        mid_point = width // 2
        left_half = image[:, :mid_point, :]  # Left half
        right_half = image[:, mid_point:, :]  # Right half

        # Perform OCR on each half and select the lower box
        detected_texts = []
        texts_only = []
        left_bbox = None
        right_bbox = None

        # OCR on left half
        left_results = self.ocr.ocr(left_half, cls=True)
        if left_results and left_results[0]:
            left_text, left_prob, left_bbox = self.get_lower_box(left_results)
            if left_text:
                detected_texts.append((left_text, left_prob))
                texts_only.append(left_text)

        # OCR on right half
        right_results = self.ocr.ocr(right_half, cls=True)
        if right_results and right_results[0]:
            right_text, right_prob, right_bbox = self.get_lower_box(right_results)
            if right_text:
                detected_texts.append((right_text, right_prob))
                texts_only.append(right_text)

        # Combine the halves back for visualization
        combined_image = np.hstack((left_half, right_half))

        # Draw bounding boxes on the combined image
        if left_bbox is not None:
            left_bbox = np.array(left_bbox).astype(int)
            cv2.polylines(combined_image, [left_bbox], isClosed=True, color=(0, 255, 0), thickness=1)
        if right_bbox is not None:
            right_bbox = np.array(right_bbox).astype(int)
            right_bbox[:, 0] += mid_point  # Shift x-coordinates to match combined image
            cv2.polylines(combined_image, [right_bbox], isClosed=True, color=(0, 255, 0), thickness=1)

        debug_url = self.save_debug_image(combined_image, detected_texts)
        return [detected_texts, texts_only, debug_url]
        
    @staticmethod
    def clean_text(texts):
        tmp = []
        for t in texts:
            t = t.replace(' ','')
            if not(ord(t[0]) >= 1569 and ord(t[0]) <= 1610):
                tmp.append(t[::-1])
            else:
                tmp.append(t)
        return tmp
======================================================================

=== File: models/token.py ===
======================================================================
from app.extensions import db
from datetime import datetime

class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
======================================================================

=== File: models/user.py ===
======================================================================
from app.extensions import db, bcrypt
from enum import Enum
import base64

class UserRole(str, Enum):
    ADMIN = 'ADMIN'
    RESIDENT = 'RESIDENT'
    GATEKEEPER = 'GATEKEEPER'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.Enum(UserRole), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Define the one-to-one relationship with Resident
    resident = db.relationship('Resident', backref=db.backref('user', uselist=False), uselist=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role
        }

class Resident(db.Model):
    __tablename__ = 'residents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    face_data_ref = db.Column(db.LargeBinary, nullable=True)
    face_image = db.Column(db.LargeBinary, nullable=True)

    # Relationships
    homes = db.relationship('Home', backref='resident', lazy=True)
    cars = db.relationship('Car', backref='resident', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.user.name,
            'email': self.user.email,
            'has_face_data': self.face_data_ref is not None,
            'face_image': base64.b64encode(self.face_image).decode('utf-8') if self.face_image else None,
            'homes': [{
                'id': home.id,
                'section': home.home_section,
                'number': home.home_num,
                'apartment': home.home_appart
            } for home in self.homes],
            'cars': [{
                'id': car.id,
                'license_plate': car.license_plate
            } for car in self.cars]
        }

class Car(db.Model):
    __tablename__ = 'cars'
    
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer, db.ForeignKey('residents.id'), nullable=False)
    license_plate = db.Column(db.String(50), unique=True)

class Home(db.Model):
    __tablename__ = 'home'
    
    id = db.Column(db.Integer, primary_key=True)
    home_section = db.Column(db.String(20))
    home_num = db.Column(db.String(20))
    home_appart = db.Column(db.String(20))
    res_id = db.Column(db.Integer, db.ForeignKey('residents.id'), nullable=False)
======================================================================

=== File: routes/admin.py ===
======================================================================
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import numpy as np
import os
import pickle
from app.models.user import User, UserRole, Resident, Car, Home
from app.models.guest import Guest, GuestInvitation, GuestHistory, GuestStatus
from app.extensions import db
from app.config import Config
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from app.utils.helpers import allowed_file
import base64
import logging

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__)

# Use global models via current_app
facial_recognition = lambda: current_app.facial_recognition
recognizer = lambda: current_app.recognizer


@admin_bp.route('/dashboard')
@jwt_required()
def dashboard():
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'ADMIN':
        return redirect(url_for('auth.login'))
    debug_dir = os.path.join(current_app.static_folder, 'debug')
    debug_images = [f'/static/debug/{f}' for f in os.listdir(debug_dir) if f.endswith('.jpg')]
    return render_template('admin/dashboard.html', user=current_user, debug_images=debug_images)
# @admin_bp.route('/dashboard')
# def dashboard():  # No @jwt_required() here
#     return render_template('admin/dashboard.html')
# @admin_bp.route('/dashboard')
# @jwt_required()
# def dashboard():
#     try:
#         current_user_id = get_jwt_identity()
#         current_user = User.query.get(current_user_id)
#         if not current_user or current_user.role != 'ADMIN':
#             return redirect(url_for('auth.login'))
#         return render_template('admin/dashboard.html', user=current_user)
#     except Exception as e:
#         return redirect(url_for('auth.login'))

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 403
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    if data.get('password'):
        user.set_password(data['password'])
    user.role = data.get('role', user.role)
    db.session.commit()
    return jsonify({'message': 'User updated', 'user': user.to_dict()}), 200

@admin_bp.route('/residents/<int:resident_id>', methods=['PUT'])
@jwt_required()
def update_resident(resident_id):
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 403
    resident = Resident.query.get_or_404(resident_id)
    data = request.get_json()
    user = resident.user
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify({'message': 'Resident updated', 'resident': resident.to_dict()}), 200

@admin_bp.route('/guests', methods=['GET'])
@jwt_required()
def get_guests():
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 403

        guests = Guest.query.all()
        return jsonify({
            'guests': [{
                'id': g.id,
                'name': g.name,
                'face_image': base64.b64encode(g.face_image).decode('utf-8') if g.face_image else None,
                'created_at': g.created_at.isoformat(),
                'resident': {
                    'id': g.resident.id,
                    'name': g.resident.user.name,
                    'email': g.resident.user.email,
                    'homes': [{
                        'section': h.home_section,
                        'number': h.home_num,
                        'apartment': h.home_appart
                    } for h in g.resident.homes]
                } if g.resident else None,
                'current_invitation': {
                    'id': inv.id,
                    'status': inv.status.value,
                    'end_date': inv.end_date.isoformat()
                } if (inv := g.get_current_invitation()) else None
            } for g in guests]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/guest/<int:guest_id>', methods=['PUT'])
@jwt_required()
def update_guest(guest_id):
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 403
    guest = Guest.query.get_or_404(guest_id)
    form = request.form
    guest.name = form.get('name', guest.name)
    if 'image' in request.files:
        image_data = request.files['image'].read()
        embedding = current_app.facial_recognition.generate_embedding(image_data)
        guest.embedding = pickle.dumps(embedding)
    if form.get('end_date'):
        invitation = guest.get_current_invitation() or GuestInvitation(guest_id=guest_id)
        invitation.end_date = datetime.strptime(form['end_date'], '%Y-%m-%d')
        db.session.add(invitation)
    db.session.commit()
    return jsonify({'message': 'Guest updated', 'guest': guest.to_dict()}), 200

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 403
        
        users = User.query.all()
        return jsonify({
            'users': [{
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'resident_data': user.resident.to_dict() if user.resident else None,
                'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None
            } for user in users]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users', methods=['POST'])
@jwt_required()
def add_user():
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.get_json()
        required_fields = ['name', 'email', 'password', 'role']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
            
        # Create new user
        new_user = User(
            name=data['name'],
            email=data['email'],
            role=data['role']
        )
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        
        if data['role'] == 'RESIDENT':
            resident = Resident(user_id=new_user.id)
            db.session.add(resident)
            db.session.commit()

        return jsonify({
            'message': 'User created successfully',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/residents', methods=['GET'])
@jwt_required()
def get_all_residents():
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 403

        residents = Resident.query.all()
        return jsonify({
            'residents': [{
                'id': r.id,
                'user_id': r.user_id,
                'name': r.user.name,
                'email': r.user.email,
                'has_face_data': r.face_data_ref is not None,
                'face_image': base64.b64encode(r.face_image).decode('utf-8') if r.face_image else None,
                'homes': [{
                    'id': h.id,
                    'section': h.home_section,
                    'number': h.home_num,
                    'apartment': h.home_appart
                } for h in r.homes],
                'cars': [{
                    'id': c.id,
                    'license_plate': c.license_plate
                } for c in r.cars],
                'guests': [{
                    'id': g.id,
                    'name': g.name,
                    'created_at': g.created_at.isoformat(),
                    'current_invitation': g.get_current_invitation().to_dict() if g.get_current_invitation() else None
                } for g in r.guests]
            } for r in residents]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# @admin_bp.route('/add_car', methods=['POST'])
# @jwt_required()
# def add_car():
#     current_user = User.query.get(get_jwt_identity())
#     if not current_user or current_user.role != 'ADMIN':
#         return jsonify({'error': 'Unauthorized'}), 403

#     resident_id = request.form.get('resident_id')
#     if not resident_id or 'image' not in request.files:
#         return jsonify({'error': 'Resident ID and image are required'}), 400

#     resident = Resident.query.get(resident_id)
#     if not resident:
#         return jsonify({'error': 'Resident not found'}), 404

#     file = request.files['image']
#     if file.filename == '' or not allowed_file(file.filename):
#         return jsonify({'error': 'Invalid or no file selected'}), 400

#     try:
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
#         file.save(filepath)

#         cropped_plate = recognizer().crop_plate(filepath)
#         if cropped_plate is None:
#             return jsonify({'error': 'No license plate detected'}), 400

#         result = recognizer().detect_text(np.array(cropped_plate))
#         cleaned_texts = recognizer().clean_text(result[1])

#         car = Car(resident_id=resident_id, license_plate=cleaned_texts[0] if cleaned_texts else 'PENDING')
#         db.session.add(car)
#         db.session.commit()

#         return jsonify({
#             'status': 'success',
#             'message': 'Car added pending verification',
#             'car_id': car.id,
#             'license_plate': car.license_plate,
#             'debug_image': result[2]
#         }), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#     finally:
#         if os.path.exists(filepath):
#             os.remove(filepath)

@admin_bp.route('/resident/<int:resident_id>/home', methods=['POST'])
@jwt_required()
def add_home(resident_id):
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 403

    resident = Resident.query.get(resident_id)
    if not resident:
        return jsonify({'error': 'Resident not found'}), 404

    data = request.get_json()
    required_fields = ['section', 'number', 'apartment']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    home = Home(
        home_section=data['section'],
        home_num=data['number'],
        home_appart=data['apartment'],
        res_id=resident_id
    )
    db.session.add(home)
    db.session.commit()

    return jsonify({'message': 'Home added successfully', 'home_id': home.id}), 200

@admin_bp.route('/resident/<int:resident_id>/face', methods=['POST'])
@jwt_required()
def update_resident_face(resident_id):
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 403

    resident = Resident.query.get(resident_id)
    if not resident:
        return jsonify({'error': 'Resident not found'}), 404

    if 'image' not in request.files:
        return jsonify({'error': 'Image required'}), 400

    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error':'Invalid or no file selected'}), 400
    
    try:
        # Read the image data
        image_data = file.read()
        
        # Generate embedding
        embedding = facial_recognition().generate_embedding(image_data)
        if embedding is None:
            return jsonify({'error': 'Could not detect face in image'}), 400

        # Store both the embedding and the original image
        resident.face_data_ref = pickle.dumps(embedding)
        resident.face_image = image_data

        db.session.commit()
        
        return jsonify({
            'message': 'Face data updated successfully',
            'resident_id': resident_id,
            'has_face_data': True,
            'face_image': base64.b64encode(image_data).decode('utf-8')
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating resident face: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/guest/<int:guest_id>/face', methods=['POST'])
@jwt_required()
def update_guest_face(guest_id):
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 403

    guest = Guest.query.get(guest_id)
    if not guest:
        return jsonify({'error': 'Guest not found'}), 404

    if 'image' not in request.files:
        return jsonify({'error': 'Image required'}), 400

    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error':'Invalid or no file selected'}), 400
    
    try:
        # Read the image data
        image_data = file.read()
        
        # Generate embedding
        embedding = facial_recognition().generate_embedding(image_data)
        if embedding is None:
            return jsonify({'error': 'Could not detect face in image'}), 400

        # Store both the embedding and the original image
        guest.embedding = pickle.dumps(embedding)
        guest.face_image = image_data

        db.session.commit()
        
        return jsonify({
            'message': 'Face data updated successfully',
            'guest_id': guest_id,
            'face_image': base64.b64encode(image_data).decode('utf-8')
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating guest face: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/resident/<int:resident_id>/guest', methods=['POST'])
@jwt_required()
def add_guest(resident_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user or user.role != 'ADMIN':
        logger.info(f"Unauthorized access attempt by user ID: {current_user_id}")
        return jsonify({'error': 'Unauthorized'}), 403

    # Check for resident directly using Resident model
    resident = Resident.query.get(resident_id)
    if not resident:
        logger.info(f"Resident ID {resident_id} not found")
        return jsonify({'error': 'Resident not found'}), 404

    try:
        name = request.form.get('name')
        if not name:
            logger.error("Name is required")
            return jsonify({'error': 'Name is required'}), 400

        end_date_str = request.form.get('end_date')
        end_date = None
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = datetime.now() + timedelta(days=1)

        if 'image' not in request.files:
            logger.error("No image provided")
            return jsonify({'error': 'Image is required'}), 400

        image_data = request.files['image'].read()
        if not image_data:
            logger.error("Empty image uploaded")
            return jsonify({'error': 'No image data'}), 400

        # Generate embedding
        embedding = facial_recognition().generate_embedding(image_data)
        if embedding is None:
            logger.error("Failed to generate face embedding")
            return jsonify({'error': 'Could not detect face in image'}), 400

        # Create new guest
        new_guest = Guest(
            name=name,
            embedding=pickle.dumps(embedding),
            face_image=image_data,
            resident_id=resident_id
        )
        db.session.add(new_guest)
        db.session.flush()  # Get the new guest ID

        # Create invitation
        invitation = GuestInvitation(
            guest_id=new_guest.id,
            start_date=datetime.now(),
            end_date=end_date,
            status=GuestStatus.PENDING
        )
        db.session.add(invitation)
        db.session.commit()

        logger.info(f"Guest added for resident ID {resident_id}")
        return jsonify({
            'status': 'success',
            'message': 'Guest added successfully',
            'guest': {
                'id': new_guest.id,
                'name': new_guest.name,
                'resident_id': new_guest.resident_id,
                'created_at': new_guest.created_at.isoformat(),
                'invitation': {
                    'id': invitation.id,
                    'end_date': invitation.end_date.isoformat(),
                    'status': invitation.status.value
                }
            }
        }), 200

    except ValueError as e:
        logger.error(f"ValueError adding guest: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error adding guest: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/guest/<int:guest_id>/invitation', methods=['POST'])
@jwt_required()
def add_invitation(guest_id):
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 403

    guest = Guest.query.get(guest_id)
    if not guest:
        return jsonify({'error': 'Guest not found'}), 404

    data = request.get_json()
    end_date_str = data.get('end_date')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else datetime.now() + timedelta(days=1)

    invitation = GuestInvitation(guest_id=guest_id, end_date=end_date, status=GuestStatus.PENDING)
    db.session.add(invitation)
    db.session.commit()

    return jsonify({'message': 'Invitation added', 'invitation_id': invitation.id}), 200

@admin_bp.route('/guest/<int:guest_id>/history', methods=['GET'])
@jwt_required()
def view_guest_history(guest_id):
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 403

    guest = Guest.query.get(guest_id)
    if not guest:
        return jsonify({'error': 'Guest not found'}), 404

    history = GuestHistory.query.filter_by(guest_id=guest_id).all()
    return jsonify({
        'guest_name': guest.name,
        'history': [{'id': h.id, 'timestamp': h.timestamp.isoformat(), 'invitation_id': h.invitation_id} for h in history]
    }), 200

@admin_bp.route('/verify_guest_face', methods=['POST'])
@jwt_required()
def verify_guest_face():
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 403

    if 'image' not in request.files:
        return jsonify({'error': 'Image required'}), 400

    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid or no file selected'}), 400

    try:
        # Read and encode the uploaded image for comparison display
        image_data = file.read()
        uploaded_image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        # Generate embedding for the uploaded image
        test_embedding = facial_recognition().generate_embedding(image_data)
        if test_embedding is None:
            return jsonify({'error': 'No face detected in uploaded image'}), 400

        # Find the best match among all guests
        guests = Guest.query.all()
        min_distance = float('inf')
        best_match = None

        for guest in guests:
            stored_embedding = pickle.loads(guest.embedding)
            distance = np.linalg.norm(test_embedding - stored_embedding)
            if distance < min_distance:
                min_distance = distance
                best_match = guest

        threshold = 0.8  # Adjust this threshold based on your needs
        if min_distance < threshold and best_match:
            current_invitation = best_match.get_current_invitation()
            resident = best_match.resident
            
            return jsonify({
                'match_found': True,
                'distance': float(min_distance),
                'uploaded_image': uploaded_image_b64,
                'guest': {
                    'id': best_match.id,
                    'name': best_match.name,
                    'face_image': base64.b64encode(best_match.face_image).decode('utf-8'),
                    'created_at': best_match.created_at.isoformat(),
                    'resident': {
                        'id': resident.id,
                        'name': resident.user.name,
                        'email': resident.user.email,
                        'homes': [{
                            'section': h.home_section,
                            'number': h.home_num,
                            'apartment': h.home_appart
                        } for h in resident.homes]
                    } if resident else None,
                    'current_invitation': {
                        'id': current_invitation.id,
                        'start_date': current_invitation.start_date.isoformat(),
                        'end_date': current_invitation.end_date.isoformat(),
                        'status': current_invitation.status.value,
                        'created_at': current_invitation.created_at.isoformat()
                    } if current_invitation else None,
                    'all_invitations': [{
                        'id': inv.id,
                        'start_date': inv.start_date.isoformat(),
                        'end_date': inv.end_date.isoformat(),
                        'status': inv.status.value,
                        'created_at': inv.created_at.isoformat()
                    } for inv in best_match.invitations],
                    'history': [{
                        'id': h.id,
                        'timestamp': h.timestamp.isoformat(),
                        'invitation_id': h.invitation_id
                    } for h in best_match.history]
                }
            }), 200
        else:
            return jsonify({
                'match_found': False,
                'message': 'No matching face found',
                'distance': float(min_distance),
                'uploaded_image': uploaded_image_b64,
                'threshold': threshold
            }), 200

    except Exception as e:
        logger.error(f"Error in verify_guest_face: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error processing face verification',
            'details': str(e)
        }), 500

# @admin_bp.route('/guest/<int:guest_id>/car', methods=['POST'])
# @jwt_required()
# def add_guest_car(guest_id):
#     current_user = User.query.get(get_jwt_identity())
#     if not current_user or current_user.role != 'ADMIN':
#         return jsonify({'error': 'Unauthorized'}), 403

#     guest = Guest.query.get(guest_id)
#     if not guest:
#         return jsonify({'error': 'Guest not found'}), 404

#     if 'image' not in request.files:
#         return jsonify({'error': 'Image required'}), 400

#     file = request.files['image']
#     if file.filename == '' or not allowed_file(file.filename):
#         return jsonify({'error': 'Invalid or no file selected'}), 400

#     try:
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
#         file.save(filepath)

#         cropped_plate = recognizer().crop_plate(filepath)
#         if cropped_plate is None:
#             return jsonify({'error': 'No license plate detected'}), 400

#         result = recognizer().detect_text(np.array(cropped_plate))
#         cleaned_texts = recognizer().clean_text(result[1])

#         # Placeholder for guest car (consider adding a GuestCar model)
#         return jsonify({
#             'status': 'success',
#             'message': 'Car added pending verification',
#             'guest_id': guest_id,
#             'license_plate': cleaned_texts[0] if cleaned_texts else 'PENDING',
#             'debug_image': result[2]
#         }), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#     finally:
#         if os.path.exists(filepath):
#             os.remove(filepath)

@admin_bp.route('/verify_resident_face', methods=['POST'])
@jwt_required()
def verify_resident_face():
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 403

    if 'image' not in request.files:
        return jsonify({'error': 'Image required'}), 400

    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid or no file selected'}), 400

    image_data = file.read()
    try:
        test_embedding = facial_recognition().generate_embedding(image_data)
        residents = Resident.query.filter(Resident.face_data_ref.isnot(None)).all()
        min_distance = float('inf')
        best_match = None

        for resident in residents:
            stored_embedding = pickle.loads(resident.face_data_ref)
            distance = np.linalg.norm(test_embedding - stored_embedding)
            if distance < min_distance:
                min_distance = distance
                best_match = resident

        threshold = 0.8
        if min_distance < threshold and best_match:
            return jsonify({
                'resident_id': best_match.id,
                'name': best_match.user.name,
                'email': best_match.user.email,
                'face_image': base64.b64encode(best_match.face_image).decode('utf-8') if best_match.face_image else None,
                'distance': float(min_distance),
                'homes': [{
                    'section': h.home_section,
                    'number': h.home_num,
                    'apartment': h.home_appart
                } for h in best_match.homes],
                'cars': [{
                    'license_plate': c.license_plate
                } for c in best_match.cars]
            }), 200
        return jsonify({'message': 'No match found', 'distance': float(min_distance)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/resident', methods=['POST'])
@jwt_required()
def add_resident():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user or user.role != 'ADMIN':
        logger.info(f"Unauthorized access attempt by user ID: {current_user_id}")
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        data = request.get_json()
        logger.info(f"Adding new resident with data: {data}")
        if not data or 'email' not in data or 'password' not in data or 'name' not in data:
            return jsonify({'error': 'Email, password, and name are required'}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400

        new_resident = User(email=data['email'], name=data['name'], role='RESIDENT')
        new_resident.set_password(data['password'])
        db.session.add(new_resident)
        db.session.commit()
        logger.info(f"Resident added: {new_resident.email}")
        return jsonify({'message': 'Resident added', 'user': new_resident.to_dict()}), 201
    except Exception as e:
        logger.error(f"Error adding resident: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/guest/<int:guest_id>/invitations', methods=['GET'])
@jwt_required()
def get_guest_invitations(guest_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 403

        guest = Guest.query.get_or_404(guest_id)
        invitations = GuestInvitation.query.filter_by(guest_id=guest_id).order_by(GuestInvitation.created_at.desc()).all()

        return jsonify({
            'guest': {
                'id': guest.id,
                'name': guest.name,
                'face_image': base64.b64encode(guest.face_image).decode('utf-8') if guest.face_image else None,
            },
            'invitations': [{
                'id': inv.id,
                'status': inv.status.value,
                'start_date': inv.start_date.isoformat(),
                'end_date': inv.end_date.isoformat(),
                'created_at': inv.created_at.isoformat()
            } for inv in invitations]
        }), 200

    except Exception as e:
        logger.error(f"Error getting guest invitations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/invitation/<int:invitation_id>', methods=['DELETE'])
@jwt_required()
def delete_invitation(invitation_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 403

        invitation = GuestInvitation.query.get_or_404(invitation_id)
        
        # Store guest_id before deletion for response
        guest_id = invitation.guest_id
        
        db.session.delete(invitation)
        db.session.commit()

        return jsonify({
            'message': 'Invitation deleted successfully',
            'guest_id': guest_id
        }), 200

    except Exception as e:
        logger.error(f"Error deleting invitation: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/add_car', methods=['POST'])
@jwt_required()
def add_car():
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    resident_id = data.get('resident_id')
    license_plate = data.get('license_plate')

    if not resident_id or not license_plate:
        return jsonify({'error': 'Resident ID and license plate are required'}), 400

    resident = Resident.query.get(resident_id)
    if not resident:
        return jsonify({'error': 'Resident not found'}), 404

    try:
        # Check if license plate already exists
        existing_car = Car.query.filter_by(license_plate=license_plate).first()
        if existing_car:
            return jsonify({'error': 'License plate already registered'}), 400

        car = Car(resident_id=resident_id, license_plate=license_plate)
        db.session.add(car)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Car added successfully',
            'car_id': car.id,
            'license_plate': car.license_plate
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.exception("Error adding car")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/guest/<int:guest_id>/car', methods=['POST'])
@jwt_required()
def add_guest_car(guest_id):
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    license_plate = data.get('license_plate')

    if not license_plate:
        return jsonify({'error': 'License plate is required'}), 400

    guest = Guest.query.get(guest_id)
    if not guest:
        return jsonify({'error': 'Guest not found'}), 404

    try:
        # Here you might want to add the car to a GuestCar table
        # For now, we'll just return success
        return jsonify({
            'status': 'success',
            'message': 'Guest car registered successfully',
            'guest_id': guest_id,
            'license_plate': license_plate
        }), 200
    except Exception as e:
        logger.exception("Error adding guest car")
        return jsonify({'error': str(e)}), 500

# @admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
# @jwt_required()
# def delete_user(user_id):
#     try:
#         current_user = User.query.get(get_jwt_identity())
#         if not current_user or current_user.role != 'ADMIN':
#             return jsonify({'error': 'Unauthorized'}), 403

#         user = User.query.get(user_id)
#         if not user:
#             return jsonify({'error': 'User not found'}), 404

#         db.session.delete(user)
#         db.session.commit()

#         return jsonify({'message': 'User deleted successfully'})
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500
======================================================================

=== File: routes/api.py ===
======================================================================
from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.guest import Guest, GuestInvitation, GuestStatus  
from app.config import Config
from werkzeug.utils import secure_filename
import os
import numpy as np 
import pickle
from datetime import datetime, timedelta  
from app.utils.helpers import allowed_file
import logging
from PIL import Image
import base64

# Create the Blueprint
api_bp = Blueprint('api', __name__)

logger = logging.getLogger(__name__)

# Use app.facial_recognition and app.recognizer instead of local instances
facial_recognition = lambda: current_app.facial_recognition
recognizer = lambda: current_app.recognizer

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


# @api_bp.route('/recognize', methods=['POST'])
# def recognize_plate():
#     if 'image' not in request.files:
#         return jsonify({'error': 'No image file provided'}), 400

#     file = request.files['image']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     if file and allowed_file(file.filename):
#         try:
#             # Save uploaded file
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
#             file.save(filepath)

#             # Process image
#             cropped_plate = recognizer().crop_plate(filepath)
            
#             if cropped_plate is None:
#                 return jsonify({'error': 'No license plate detected'}), 400

#             # Detect text
#             result = recognizer().detect_text(np.array(cropped_plate))
#             cleaned_texts = recognizer().clean_text(result[1])

#             return jsonify({
#                 'status': 'success',
#                 'texts': cleaned_texts,
#                 'raw_result': result,
#                 'debug_image': result[2]
#             })

#         except Exception as e:
#             return jsonify({'error in /api/recognize ': str(e)}), 500

#         finally:
#             # Cleanup uploaded file
#             if os.path.exists(filepath):
#                 os.remove(filepath)

#     return jsonify({'error': 'Invalid file type'}), 400

# @api_bp.route('/recognize', methods=['POST'])
# def recognize_plate():
#     logger.info("Received request to /api/recognize")
    
#     if 'image' not in request.files:
#         logger.info("No image file provided in request")
#         return jsonify({'error': 'No image file provided'}), 400

#     file = request.files['image']
#     if file.filename == '':
#         logger.info("No selected file (empty filename)")
#         return jsonify({'error': 'No selected file'}), 400

#     if file and allowed_file(file.filename):
#         try:
#             # Save uploaded file
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
#             logger.debug(f"Saving file to {filepath}")
#             file.save(filepath)
            
#             # Verify file exists and has content
#             if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
#                 logger.info(f"File {filepath} is missing or empty")
#                 raise Exception("Saved file is missing or empty")

#             # Process image
#             logger.debug("Cropping plate")
#             cropped_plate = recognizer().crop_plate(filepath)
#             if cropped_plate is None:
#                 logger.info("No license plate detected in image")
#                 return jsonify({'error': 'No license plate detected'}), 400

#             # Convert to numpy array and detect text
#             logger.info("Detecting text")
#             result = recognizer().detect_text(np.array(cropped_plate))
#             cleaned_texts = recognizer().clean_text(result[1])

#             logger.info(f"Recognition successful: {cleaned_texts}")
#             return jsonify({
#                 'status': 'success',
#                 'texts': cleaned_texts,
#                 'raw_result': result,
#                 'debug_image': result[2]
#             })

#         except Exception as e:
#             logger.info(f"Error processing image: {str(e)}")
#             return jsonify({'error': str(e)}), 500

#         finally:
#             # Cleanup uploaded file
#             if os.path.exists(filepath):
#                 logger.info(f"Removing temporary file {filepath}")
#                 os.remove(filepath)

#     logger.info(f"Invalid file type: {file.filename}")
#     return jsonify({'error': 'Invalid file type'}), 400
# @api_bp.route('/recognize', methods=['POST'])
# def recognize_plate():
#     logger.info("Received request to /api/recognize")
    
#     if 'image' not in request.files:
#         logger.error("No image file provided in request")
#         return jsonify({'error': 'No image file provided'}), 400

#     file = request.files['image']
#     if file.filename == '':
#         logger.error("No selected file (empty filename)")
#         return jsonify({'error': 'No selected file'}), 400

#     if file and allowed_file(file.filename):
#         try:
#             # Save uploaded file
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
#             logger.info(f"Saving file to {filepath}")
#             file.save(filepath)
            
#             # Verify file exists and has content
#             if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
#                 logger.error(f"File {filepath} is missing or empty")
#                 raise Exception("Saved file is missing or empty")

#             # Check recognizer initialization
#             if recognizer() is None:
#                 logger.error("Recognizer is not initialized")
#                 raise Exception("License plate recognizer not initialized")

#             # Process image
#             logger.info("Cropping plate")
#             cropped_plate = recognizer().crop_plate(filepath)
#             if cropped_plate is None:
#                 logger.error("No license plate detected in image")
#                 return jsonify({'error': 'No license plate detected'}), 400

#             # Log cropped plate details
#             from PIL import Image  # Ensure this is imported
#             logger.info(f"Cropped plate type: {type(cropped_plate)}, size: {cropped_plate.size if isinstance(cropped_plate, Image.Image) else 'N/A'}")

#             # Detect text
#             logger.info("Detecting text")
#             result = recognizer().detect_text(cropped_plate)
#             if not isinstance(result, list) or len(result) != 3:
#                 logger.error(f"Invalid result format from detect_text: {result}")
#                 raise Exception("Text detection returned invalid result")

#             detected_texts, texts_only, debug_url = result
#             cleaned_texts = recognizer().clean_text(texts_only)

#             logger.info(f"Recognition successful: {cleaned_texts}")
#             return jsonify({
#                 'status': 'success',
#                 'texts': cleaned_texts,
#                 'raw_result': detected_texts,
#                 'debug_image': debug_url
#             })

#         except Exception as e:
#             logger.exception(f"Error processing image: {str(e)}")
#             return jsonify({'error': str(e)}), 500

#         finally:
#             # Cleanup uploaded file
#             if os.path.exists(filepath):
#                 logger.info(f"Removing temporary file {filepath}")
#                 os.remove(filepath)

#     logger.error(f"Invalid file type: {file.filename}")
#     return jsonify({'error': 'Invalid file type'}), 400

# app/routes/api.py

# @api_bp.route('/recognize', methods=['POST'])
# def recognize_plate():
#     logger.info("Received request to /api/recognize")
    
#     if 'image' not in request.files:
#         logger.error("No image file provided in request")
#         return jsonify({'error': 'No image file provided'}), 400

#     file = request.files['image']
#     if file.filename == '':
#         logger.error("No selected file (empty filename)")
#         return jsonify({'error': 'No selected file'}), 400

#     if file and allowed_file(file.filename):
#         try:
#             # Save uploaded file
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
#             logger.info(f"Saving file to {filepath}")
#             file.save(filepath)
            
#             # Verify file exists and has content
#             if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
#                 logger.error(f"File {filepath} is missing or empty")
#                 raise Exception("Saved file is missing or empty")

#             # Check recognizer initialization
#             if recognizer() is None:
#                 logger.error("Recognizer is not initialized")
#                 raise Exception("License plate recognizer not initialized")

#             # Process image
#             logger.info("Cropping plate")
#             cropped_plate = recognizer().crop_plate(filepath)
#             if cropped_plate is None:
#                 logger.error("No license plate detected in image")
#                 return jsonify({'error': 'No license plate detected'}), 400

#             # Detect text
#             logger.info("Detecting text")
#             result = recognizer().detect_text(cropped_plate)
#             if not isinstance(result, list) or len(result) != 3:
#                 logger.error(f"Invalid result format from detect_text: {result}")
#                 raise Exception("Text detection returned invalid result")

#             detected_texts, texts_only, debug_url = result
#             cleaned_texts = recognizer().clean_text(texts_only)
#             logger.info(f"OCR OUTPUT:{result} cleaned_texts:{cleaned_texts}")

#             # Convert debug image to base64
#             debug_image_path = os.path.join(current_app.root_path, debug_url.lstrip('/'))
#             with open(debug_image_path, "rb") as image_file:
#                 debug_image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

#             # cleaned_texts=cleaned_texts.join(' ')
#             final=f"{cleaned_texts[0]}{cleaned_texts[1]}"
#             logger.info(f"Recognition successful: {final}")
#             return jsonify({
#                 'status': 'success',
#                 'texts': final,
#                 'raw_result': detected_texts,
#                 'debug_image': debug_image_base64,
#                 'debug_url': debug_url
#             })

#         except Exception as e:
#             logger.exception(f"Error processing image: {str(e)}")
#             return jsonify({'error': str(e)}), 500

#         finally:
#             # Cleanup uploaded file
#             if os.path.exists(filepath):
#                 logger.info(f"Removing temporary file {filepath}")
#                 os.remove(filepath)

#     logger.error(f"Invalid file type: {file.filename}")
#     return jsonify({'error': 'Invalid file type'}), 400

@api_bp.route('/recognize', methods=['POST'])
def recognize_plate():
    logger.info("Received request to /api/recognize")
    
    if 'image' not in request.files:
        logger.error("No image file provided in request")
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        logger.error("No selected file (empty filename)")
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            # Save uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            logger.info(f"Saving file to {filepath}")
            file.save(filepath)
            
            # Verify file exists and has content
            if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                logger.error(f"File {filepath} is missing or empty")
                raise Exception("Saved file is missing or empty")

            # Check recognizer initialization
            if recognizer() is None:
                logger.error("Recognizer is not initialized")
                raise Exception("License plate recognizer not initialized")

            # Process image
            logger.info("Cropping plate")
            cropped_plate = recognizer().crop_plate(filepath)
            if cropped_plate is None:
                logger.error("No license plate detected in image")
                return jsonify({'error': 'No license plate detected'}), 400

            # Convert PIL Image to numpy array
            import numpy as np
            cropped_plate_np = np.array(cropped_plate)

            # Detect text
            logger.info("Detecting text")
            result = recognizer().detect_text(cropped_plate_np)  # Pass numpy array instead of PIL Image
            if not isinstance(result, list) or len(result) != 3:
                logger.error(f"Invalid result format from detect_text: {result}")
                raise Exception("Text detection returned invalid result")

            detected_texts, texts_only, debug_url = result
            cleaned_texts = recognizer().clean_text(texts_only)
            logger.info(f"OCR OUTPUT:{result} cleaned_texts:{cleaned_texts}")

            # Convert debug image to base64
            debug_image_path = os.path.join(current_app.root_path, debug_url.lstrip('/'))
            with open(debug_image_path, "rb") as image_file:
                debug_image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

            final = f"{cleaned_texts[1][::-1]}{cleaned_texts[0]}"
            logger.info(f"Recognition successful: {final}")
            return jsonify({
                'status': 'success',
                'texts': final,
                'raw_result': detected_texts,
                'debug_image': debug_image_base64,
                'debug_url': debug_url
            })

        except Exception as e:
            logger.exception(f"Error processing image: {str(e)}")
            return jsonify({'error': str(e)}), 500

        finally:
            # Cleanup uploaded file
            if os.path.exists(filepath):
                logger.info(f"Removing temporary file {filepath}")
                os.remove(filepath)

    logger.error(f"Invalid file type: {file.filename}")
    return jsonify({'error': 'Invalid file type'}), 400

@api_bp.route('/add_guest', methods=['POST'])
def add_guest():
    try:
        name = request.form.get('name')
        if not name:
            return jsonify({'error': 'Name is required'}), 400

        # Get end date for invitation (optional)
        end_date_str = request.form.get('end_date')
        end_date = None
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            # Default to 1 day invitation
            end_date = datetime.now() + timedelta(days=1)

        # Get image data
        if 'image' in request.files:
            image_data = request.files['image'].read()
        else:
            image_data = request.form.get('image_data')
            if not image_data:
                return jsonify({'error': 'Image is required'}), 400

        # Generate embedding
        embedding = facial_recognition().generate_embedding(image_data)
        
        # Save to database
        result = Guest.add_guest(name, embedding, end_date)
        
        return jsonify({
            'status': result['status'],
            'message': result['message'],
            'guest': {
                'id': result['guest'].id,
                'name': result['guest'].name,
                'created_at': result['guest'].created_at.isoformat(),
                'current_invitation': {
                    'id': result['invitation'].id if 'invitation' in result else None,
                    'start_date': result['invitation'].start_date.isoformat() if 'invitation' in result else None,
                    'end_date': result['invitation'].end_date.isoformat() if 'invitation' in result else None,
                    'status': result['invitation'].status.value if 'invitation' in result else None
                } if 'invitation' in result else None
            }
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/validate_face', methods=['POST'])
def validate_face():
    try:
        # Get image data
        if 'image' in request.files:
            image_data = request.files['image'].read()
        else:
            image_data = request.form.get('image_data')
            if not image_data:
                return jsonify({'error': 'Image is required'}), 400

        # Generate embedding
        test_embedding = facial_recognition().generate_embedding(image_data)
        
        # Find match using the method from Guest model
        guests = Guest.query.all()
        min_distance = float('inf')
        best_match = None

        for guest in guests:
            stored_embedding = pickle.loads(guest.embedding)
            distance = np.linalg.norm(test_embedding - stored_embedding)
            if distance < min_distance:
                min_distance = distance
                best_match = guest

        threshold = 0.8
        if min_distance < threshold and best_match:
            # Get current invitation
            current_invitation = best_match.get_current_invitation()
            
            if not current_invitation:
                return jsonify({
                    'name': best_match.name,
                    'status': 'no_active_invitation',
                    'message': 'No active invitation found',
                    'distance': float(min_distance)
                }), 200

            # Handle status update if requested
            new_status = request.form.get('status')
            status_updated = False
            status_message = "Face recognized"

            if new_status and new_status in [status.value for status in GuestStatus]:
                status_updated, status_message = best_match.update_invitation_status(
                    current_invitation.id,
                    GuestStatus(new_status)
                )

            return jsonify({
                'name': best_match.name,
                'current_invitation': {
                    'id': current_invitation.id,
                    'start_date': current_invitation.start_date.isoformat(),
                    'end_date': current_invitation.end_date.isoformat(),
                    'status': current_invitation.status.value
                },
                'status_message': status_message,
                'status_updated': status_updated,
                'distance': float(min_distance),
                'history': [{
                    'timestamp': h.timestamp.isoformat(),
                    'invitation_id': h.invitation_id
                } for h in best_match.history]
            }), 200
        else:
            return jsonify({
                'name': 'Unknown',
                'distance': float(min_distance)
            }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'facial_recognition': 'loaded' if facial_recognition() else 'not loaded',
        'license_plate_recognizer': 'loaded' if recognizer() else 'not loaded'
    })

@api_bp.route('/validate_resident_face', methods=['POST'])
def validate_resident_face():
    try:
        # Get image data
        if 'image' in request.files:
            image_data = request.files['image'].read()
        else:
            image_data = request.form.get('image_data')
            if not image_data:
                return jsonify({'error': 'Image is required'}), 400

        # Generate embedding using the existing facial_recognition structure
        test_embedding = facial_recognition().generate_embedding(image_data)
        
        # Find match among residents (assuming a Resident model exists)
        from app.models.resident import Resident  # Import here to avoid circular imports
        residents = Resident.query.all()
        min_distance = float('inf')
        best_match = None

        for resident in residents:
            stored_embedding = pickle.loads(resident.embedding)
            distance = np.linalg.norm(test_embedding - stored_embedding)
            if distance < min_distance:
                min_distance = distance
                best_match = resident

        threshold = 0.8  # Same threshold as validate_face
        if min_distance < threshold and best_match:
            return jsonify({
                'name': best_match.name,
                'distance': float(min_distance)
            }), 200
        else:
            return jsonify({
                'name': 'Unknown',
                'distance': float(min_distance)
            }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@api_bp.route('/residents/search', methods=['GET'])
def search_resident_by_plate():
    plate = request.args.get('license_plate')
    if not plate:
        return jsonify({'error': 'License plate is required'}), 400

    from app.models.resident import Resident  # Import here to avoid circular imports
    resident = Resident.query.filter_by(license_plate=plate).first()
    if resident:
        return jsonify({
            'status': 'success',
            'resident': {
                'id': resident.id,
                'name': resident.name,
                'license_plate': resident.license_plate
            }
        }), 200
    else:
        return jsonify({
            'status': 'not_found',
            'message': 'No resident found with this license plate'
        }), 404

@api_bp.route('/guests/search', methods=['GET'])
def search_guest_by_plate():
    plate = request.args.get('license_plate')
    if not plate:
        return jsonify({'error': 'License plate is required'}), 400

    guest = Guest.query.filter_by(license_plate=plate).first()
    if guest:
        current_invitation = guest.get_current_invitation()
        return jsonify({
            'status': 'success',
            'guest': {
                'id': guest.id,
                'name': guest.name,
                'license_plate': guest.license_plate,
                'current_invitation': {
                    'id': current_invitation.id,
                    'start_date': current_invitation.start_date.isoformat(),
                    'end_date': current_invitation.end_date.isoformat(),
                    'status': current_invitation.status.value
                } if current_invitation else None
            }
        }), 200
    else:
        return jsonify({
            'status': 'not_found',
            'message': 'No guest found with this license plate'
        }), 404


======================================================================

=== File: routes/auth.py ===
======================================================================
from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import (
    create_access_token, 
    set_access_cookies,
    jwt_required, 
    get_jwt_identity, 
    get_jwt
)
from app.models.user import User, UserRole
from app.models.token import TokenBlocklist
from app.extensions import db, bcrypt
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger('app')

# @auth_bp.route('/login', methods=['GET'])
# def login_page():
#     return render_template('auth/login.html')

# @auth_bp.route('/login', methods=['POST'])
# def login():
#     try:
#         logger.info("Processing login request")
        
#         # Log raw request data
#         logger.info(f"Request data: {request.get_data()}")
#         data = request.get_json()
#         logger.info(f"Parsed JSON data: {data}")
        
#         if not data or not data.get('email') or not data.get('password'):
#             logger.warning("Missing email or password in request")
#             return jsonify({'error': 'Missing email or password'}), 400
        
#         # Log email being checked
#         email = data.get('email')
#         logger.info(f"Attempting login for email: {email}")
        
#         user = User.query.filter_by(email=email).first()
#         if not user:
#             logger.warning(f"No user found with email: {email}")
#             return jsonify({'error': 'Invalid email or password'}), 401
        
#         logger.info(f"Found user: {user.email}, role: {user.role}")
        
#         # Log password check
#         password = data.get('password')
#         password_check = user.check_password(password)
#         logger.info(f"Password check result: {password_check}")
        
#         if not password_check:
#             logger.warning("Invalid password provided")
#             return jsonify({'error': 'Invalid email or password'}), 401
        
#         # Create tokens
#         access_token = create_access_token(identity=str(user.id))
#         # refresh_token = create_refresh_token(identity=str(user.id))
        
#         response_data = {
#             'message': 'Login successful',
#             'access_token': access_token,
#             # 'refresh_token': refresh_token,
#             'user': user.to_dict()
#         }
#         set_access_cookies(response, access_token)  # Set token in cookie
#         logger.info(f"Login successful for user: {user.email}")
#         logger.info(f"Response data: {response_data}")
        
#         return jsonify(response_data), 200
        
#     except Exception as e:
#         logger.error(f"Login error: {str(e)}", exc_info=True)
#         return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        logger.info("Serving login page")
        return render_template('auth/login.html')

    logger.info("Processing login request")
    logger.info(f"Raw request data: {request.data}")
    logger.info(f"Content-Type header: {request.headers.get('Content-Type')}")
    try:
        data = request.get_json()
        logger.info(f"Parsed request data: {data}")
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Invalid JSON payload'}), 400

    if not data or 'email' not in data or 'password' not in data:
        logger.error("Missing email or password in request")
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        logger.info(f"Invalid credentials for email: {data['email']}")
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=str(user.id))
    response = jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    })
    set_access_cookies(response, access_token)
    logger.info(f"Login successful for user: {user.email}")
    return response, 200


@auth_bp.route('/check_token', methods=['GET'])
@jwt_required()
def check_token():
    try:
        logger.info("/check_token send")
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({
            'valid': True,
            'user': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 401

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({'message': 'Logout successful'})
    response.delete_cookie('access_token_cookie')
    response.delete_cookie('csrf_access_token')
    return response, 200
    # try:
    #     jti = get_jwt()['jti']
    #     user_id = int(get_jwt_identity())
        
    #     token_block = TokenBlocklist(jti=jti, user_id=user_id)
    #     db.session.add(token_block)
    #     db.session.commit()
        
    #     return jsonify({'message': 'Successfully logged out'}), 200
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        return jsonify({'access_token': access_token}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/test_auth', methods=['POST'])
def test_auth():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            })
            
        password_check = user.check_password(password)
        
        return jsonify({
            'status': 'success',
            'email': email,
            'stored_hash': user.password_hash,
            'password_check': password_check
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })
======================================================================

=== File: routes/gatekeeper.py ===
======================================================================
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

gatekeeper_bp = Blueprint('gatekeeper', __name__)


@gatekeeper_bp.route('/dashboard')
@jwt_required()
def dashboard():
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'GATEKEEPER':
        return redirect(url_for('auth.login'))
    return render_template('gatekeeper/dashboard.html', user=current_user)

======================================================================

=== File: routes/__init__.py ===
======================================================================

======================================================================

=== File: routes/resident.py ===
======================================================================
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User, UserRole, Resident
from app.extensions import db

resident_bp = Blueprint('resident', __name__)

@resident_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role != UserRole.RESIDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        resident = current_user.resident
        if not resident:
            return jsonify({'error': 'Resident profile not found'}), 404

        return jsonify({
            'id': resident.id,
            'name': current_user.name,
            'email': current_user.email,
            'has_face_data': resident.face_data_ref is not None,
            'homes': [{
                'section': h.home_section,
                'number': h.home_num,
                'apartment': h.home_appart
            } for h in resident.homes],
            'cars': [{
                'license_plate': c.license_plate
            } for c in resident.cars]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@resident_bp.route('/face', methods=['POST'])
@jwt_required()
def update_face():
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role != UserRole.RESIDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        if not current_user.resident:
            return jsonify({'error': 'Resident profile not found'}), 404

        if 'face_data' not in request.files:
            return jsonify({'error': 'No face data provided'}), 400

        face_data = request.files['face_data'].read()
        current_user.resident.face_data_ref = face_data
        db.session.commit()

        return jsonify({
            'message': 'Face data updated successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
======================================================================

=== File: utils/auth.py ===
======================================================================
from functools import wraps
from flask import redirect, url_for
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except:
            return redirect(url_for('home'))
    return decorated
======================================================================

=== File: utils/helpers.py ===
======================================================================
from app.config import Config

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

======================================================================

=== File: utils/__init__.py ===
======================================================================

======================================================================
