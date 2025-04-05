from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import numpy as np 
from datetime import datetime, timedelta  
import pickle
from app.config import Config
from app.models.license_plate_recognizer import LicensePlateRecognizer
from app.models.facial_recognition import FacialRecognition
from app.models.guest import Guest, GuestStatus  

# Create the Blueprint
api_bp = Blueprint('api', __name__)
# recognizer = LicensePlateRecognizer(Config.YOLO_MODEL_PATH, Config.DEBUG_DIR)
# facial_recognition = FacialRecognition()
try:
    recognizer = LicensePlateRecognizer(Config.YOLO_MODEL_PATH, Config.DEBUG_DIR)
    facial_recognition = FacialRecognition()
except Exception as e:
    print(f"Error initializing models: {e}")

@api_bp.route('/recognize', methods=['POST'])
def recognize_plate():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            # Save uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Process image
            cropped_plate = recognizer.crop_plate(filepath)
            
            if cropped_plate is None:
                return jsonify({'error': 'No license plate detected'}), 400

            # Detect text
            result = recognizer.detect_text(np.array(cropped_plate))
            cleaned_texts = recognizer.clean_text(result[1])

            return jsonify({
                'status': 'success',
                'texts': cleaned_texts,
                'raw_result': result,
                'debug_image': result[2]
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

        finally:
            # Cleanup uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)

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
        embedding = facial_recognition.generate_embedding(image_data)
        
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
        test_embedding = facial_recognition.generate_embedding(image_data)
        
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
        'models_loaded': {
            'license_plate': recognizer is not None,
            'facial_recognition': facial_recognition is not None
        }
    })

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS