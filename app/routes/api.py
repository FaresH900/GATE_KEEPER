from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import numpy as np 
from app.config import Config
from app.models.license_plate_recognizer import LicensePlateRecognizer
from app.models.facial_recognition import FacialRecognition
from app.models.guest import Guest, GuestStatus  

# Create the Blueprint
api = Blueprint('api', __name__)
# recognizer = LicensePlateRecognizer(Config.YOLO_MODEL_PATH, Config.DEBUG_DIR)
# facial_recognition = FacialRecognition()
try:
    recognizer = LicensePlateRecognizer(Config.YOLO_MODEL_PATH, Config.DEBUG_DIR)
    facial_recognition = FacialRecognition()
except Exception as e:
    print(f"Error initializing models: {e}")

@api.route('/recognize', methods=['POST'])
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


@api.route('/add_guest', methods=['POST'])
def add_guest():
    try:
        name = request.form.get('name')
        if not name:
            return jsonify({'error': 'Name is required'}), 400

        # Get image data
        if 'image' in request.files:
            image_data = request.files['image'].read()
        else:
            image_data = request.form.get('image_data')
            if not image_data:
                return jsonify({'error': 'Image is required'}), 400

        # Generate embedding
        embedding = facial_recognition.generate_embedding(image_data)
        
        # Try to add guest
        result = Guest.add_guest(name, embedding)
        
        return jsonify({
            'status': result['status'],
            'message': result['message'],
            'guest': {
                'id': result['guest'].id,
                'name': result['guest'].name,
                'status': result['guest'].status.value,
                'created_at': result['guest'].created_at.isoformat()
            },
            'history': [
                {
                    'timestamp': h.timestamp.isoformat()
                } for h in result['guest'].history
            ] if 'history' in result else []
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@api.route('/validate_face', methods=['POST'])
def validate_face():
    try:
        # Get image data
        if 'image' in request.files:
            image_data = request.files['image'].read()
        else:
            image_data = request.form.get('image_data')
            if not image_data:
                return jsonify({'error': 'Image is required'}), 400

        # Get optional status update
        new_status = request.form.get('status')
        
        # Generate embedding
        test_embedding = facial_recognition.generate_embedding(image_data)
        
        # Find match
        best_match, distance = Guest.find_match(test_embedding)
        
        if best_match:
            status_updated = False
            status_message = "Face recognized"

            # Check current status and handle accordingly
            if new_status:
                if best_match.status == GuestStatus.ALLOWED and new_status == 'allowed':
                    status_message = "Guest is already allowed"
                else:
                    status_updated = best_match.update_status(GuestStatus(new_status))
                    status_message = "Status updated to " + new_status if status_updated else "Status unchanged"

            return jsonify({
                'name': best_match.name,
                'status': best_match.status.value,
                'status_message': status_message,
                'status_updated': status_updated,
                'distance': float(distance),
                'history': [
                    {
                        'timestamp': h.timestamp.isoformat()
                    } for h in best_match.history
                ]
            }), 200
        else:
            return jsonify({
                'name': 'Unknown',
                'distance': float(distance),
                'status_message': "No match found"
            }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@api.route('/health', methods=['GET'])
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