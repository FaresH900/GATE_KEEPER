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

            # Log cropped plate details
            from PIL import Image  # Ensure this is imported
            logger.info(f"Cropped plate type: {type(cropped_plate)}, size: {cropped_plate.size if isinstance(cropped_plate, Image.Image) else 'N/A'}")

            # Detect text
            logger.info("Detecting text")
            result = recognizer().detect_text(cropped_plate)
            if not isinstance(result, list) or len(result) != 3:
                logger.error(f"Invalid result format from detect_text: {result}")
                raise Exception("Text detection returned invalid result")

            detected_texts, texts_only, debug_url = result
            cleaned_texts = recognizer().clean_text(texts_only)

            logger.info(f"Recognition successful: {cleaned_texts}")
            return jsonify({
                'status': 'success',
                'texts': cleaned_texts,
                'raw_result': detected_texts,
                'debug_image': debug_url
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

