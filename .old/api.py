from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.guest import Guest, GuestInvitation, GuestStatus  
from app.config import Config
from werkzeug.utils import secure_filename
import os
import cv2
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

@api_bp.route('/recognize', methods=['POST'])
def recognize_plate():
    logger.info("Received POST request to /api/recognize")
    logger.info(f"Important Headers: {dict(request.headers)}")

    if 'image' not in request.files:
        logger.error("No image file provided in request")
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        logger.error(f"Invalid file: {file.filename}")
        return jsonify({'error': 'Invalid file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    file.save(filepath)
    logger.info(f"Saving file to {filepath}")

    try:
        # Crop the plate using YOLO
        cropped_image = recognizer().crop_plate(filepath)
        if cropped_image is None:
            logger.info("No plate detected in image")
            return jsonify({'error': 'No plate detected'}), 400

        # Detect text from cropped plate
        detected_texts, texts_only, debug_url = recognizer().detect_text(cropped_image)
        logger.info(f"detection: {detected_texts}")
        logger.info(f"texts_only: {texts_only}")
        logger.info(f"dbg_url: {debug_url}")

        logger.info(f"DEBUG_DIR: {Config.DEBUG_DIR}")
        if not texts_only:
            logger.info("No text detected in cropped plate")
            return jsonify({'error': 'No text detected'}), 400

        # Clean the detected texts
        cleaned_texts = recognizer().clean_text(texts_only)
        logger.info(f"Cleaned texts: {cleaned_texts}")

        # Load debug image and convert to base64
        debug_img = cv2.imread(os.path.join(Config.DEBUG_DIR, debug_url.split('/')[-1]))
        if debug_img is None:
            logger.error(f"Failed to load debug image: {debug_url}")
            raise ValueError("Failed to load debug image")
        _, buffer = cv2.imencode('.jpg', debug_img)
        debug_image_base64 = base64.b64encode(buffer).decode('utf-8')

        final = f"{cleaned_texts[1][::-1]}{cleaned_texts[0]}"
        logger.info(f"Plate recognition successful: {final}")

        return jsonify({
            'status': 'success',
            'texts': final,  # Return cleaned texts
            'debug_image': debug_image_base64,
            'raw_result': detected_texts  # Full text with probabilities
        }), 200

    except RuntimeError as e:
        logger.exception(f"PaddleOCR RuntimeError: {str(e)}")
        return jsonify({'error': f"PaddleOCR error: {str(e)}"}), 500
    except Exception as e:
        logger.exception(f"Error processing image: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Removing temporary file {filepath}")

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'facial_recognition': 'loaded' if facial_recognition() else 'not loaded',
        'license_plate_recognizer': 'loaded' if recognizer() else 'not loaded'
    })


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

