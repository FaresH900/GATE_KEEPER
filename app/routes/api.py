from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.guest import Guest, GuestInvitation, GuestStatus  # Include GuestStatus
from app.models.user import Resident, Car
from app.config import Config
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
import pickle
import logging
from PIL import Image
import base64
from app.utils.helpers import allowed_file


api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Use app.facial_recognition and app.recognizer
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

        if not texts_only:
            logger.info("No text detected in cropped plate")
            return jsonify({'error': 'No text detected'}), 400

        # Clean the detected texts
        cleaned_texts = recognizer().clean_text(texts_only)
        logger.info(f"Cleaned texts: {cleaned_texts}")

        # Load debug image and convert to base64
        debug_filepath = os.path.join(Config.DEBUG_DIR, debug_url.split('/')[-1])
        debug_img = cv2.imread(debug_filepath)
        if debug_img is None:
            logger.error(f"Failed to load debug image: {debug_filepath}")
            raise ValueError(f"Failed to load debug image from {debug_filepath}")
        _, buffer = cv2.imencode('.jpg', debug_img)
        debug_image_base64 = base64.b64encode(buffer).decode('utf-8')

        logger.info(f"Plate recognition successful: {cleaned_texts}")
        return jsonify({
            'status': 'success',
            'texts': cleaned_texts,  # Return list
            'debug_image': debug_image_base64,
            'raw_result': detected_texts
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


@api_bp.route('/verify_face', methods=['POST'])
def verify_face():
    logger.info("Received POST request to /api/verify_face")
    if 'image' not in request.files:
        logger.error("No image file provided in request")
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if not file or file.filename == '':
        logger.error("Empty or invalid file received")
        return jsonify({'error': 'Invalid or empty image file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    file.save(filepath)
    logger.info(f"Saving face image to {filepath}")

    try:
        with open(filepath, 'rb') as f:
            image_data = f.read()
        if not image_data:
            raise ValueError("Image data is empty after saving")

        test_embedding = facial_recognition().generate_embedding(image_data)

        # Search residents
        residents = Resident.query.all()
        for resident in residents:
            if resident.face_data_ref:
                stored_embedding = pickle.loads(resident.face_data_ref)
                distance = facial_recognition().compare_embeddings(test_embedding, stored_embedding)
                if distance < 0.8:
                    logger.info(f"Matched resident: {resident.user.name}, distance: {distance}")
                    return jsonify({
                        'status': 'success',
                        'match': {
                            'type': 'resident',
                            'id': resident.id,
                            'user_id': resident.user_id,
                            'name': resident.user.name,
                            'email': resident.user.email,
                            'face_image': base64.b64encode(resident.face_image).decode('utf-8') if resident.face_image else None,
                            'has_face_data': resident.face_data_ref is not None,
                            'homes': [{
                                'section': h.home_section,
                                'number': h.home_num,
                                'apartment': h.home_appart
                            } for h in resident.homes],
                            'cars': [{'license_plate': c.license_plate} for c in resident.cars]
                        },
                        'distance': float(distance)
                    }), 200

        # Search guests
        guests = Guest.query.all()
        for guest in guests:
            if guest.embedding:
                stored_embedding = pickle.loads(guest.embedding)
                distance = facial_recognition().compare_embeddings(test_embedding, stored_embedding)
                if distance < 0.8:
                    current_invitation = guest.get_current_invitation()  # Call method
                    resident = guest.resident
                    logger.info(f"Matched guest: {guest.name}, distance: {distance}")
                    return jsonify({
                        'status': 'success',
                        'match': {
                            'type': 'guest',
                            'id': guest.id,
                            'name': guest.name,
                            'created_at': guest.created_at.isoformat(),
                            'face_image': base64.b64encode(guest.face_image).decode('utf-8') if guest.face_image else None,
                            'license_plate': guest.license_plate,
                            'current_invitation': {
                                'status': current_invitation.status.value,
                                'created_at': current_invitation.created_at.isoformat()
                            } if current_invitation else None,
                            'resident': {
                                'name': resident.user.name,
                                'email': resident.user.email
                            } if resident else None,
                            'invitations': [{'status': inv.status.value, 'created_at': inv.created_at.isoformat()} for inv in guest.invitations]
                        },
                        'distance': float(distance)
                    }), 200

        logger.info("No face match found")
        return jsonify({'status': 'no_match'}), 200
    except ValueError as e:
        logger.exception(f"Face verification error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.exception(f"Server error in face verification: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Removing temporary file {filepath}")

@api_bp.route('/search_plate', methods=['GET'])
def search_plate():
    plate = request.args.get('plate')
    if not plate:
        logger.error("No plate provided in request")
        return jsonify({'error': 'No plate provided'}), 400

    try:
        plate = plate.replace(' ', '').upper()

        residents = Resident.query.join(Car).filter(Car.license_plate == plate).all()
        guests = Guest.query.filter_by(license_plate=plate).all()

        logger.info(f"Found {len(residents)} residents and {len(guests)} guests with plate: {plate}")
        return jsonify({
            'residents': [{
                'id': r.id,
                'user_id': r.user_id,
                'name': r.user.name,
                'email': r.user.email,
                'face_image': base64.b64encode(r.face_image).decode('utf-8') if r.face_image else None,
                'has_face_data': r.face_data_ref is not None,
                'homes': [{
                    'section': h.home_section,
                    'number': h.home_num,
                    'apartment': h.home_appart
                } for h in r.homes],
                'cars': [{'license_plate': c.license_plate} for c in r.cars]
            } for r in residents],
            'guests': [{
                'id': g.id,
                'name': g.name,
                'created_at': g.created_at.isoformat(),
                'face_image': base64.b64encode(g.face_image).decode('utf-8') if g.face_image else None,
                'license_plate': g.license_plate,
                'current_invitation': {
                    'status': g.get_current_invitation().status.value,  # Call method
                    'created_at': g.get_current_invitation().created_at.isoformat()
                } if g.get_current_invitation() else None,
                'resident': {
                    'name': g.resident.user.name,
                    'email': g.resident.user.email
                } if g.resident else None,
                'invitations': [{'status': inv.status.value, 'created_at': inv.created_at.isoformat()} for inv in g.invitations]
            } for g in guests]
        }), 200
    except Exception as e:
        logger.exception(f"Error searching plate: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'facial_recognition': 'loaded' if facial_recognition() else 'not loaded',
        'license_plate_recognizer': 'loaded' if recognizer() else 'not loaded'
    })