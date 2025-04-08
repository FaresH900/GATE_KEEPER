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
    return render_template('admin/dashboard.html', user=current_user)
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


@admin_bp.route('/add_car', methods=['POST'])
@jwt_required()
def add_car():
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 403

    resident_id = request.form.get('resident_id')
    if not resident_id or 'image' not in request.files:
        return jsonify({'error': 'Resident ID and image are required'}), 400

    resident = Resident.query.get(resident_id)
    if not resident:
        return jsonify({'error': 'Resident not found'}), 404

    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid or no file selected'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)

        cropped_plate = recognizer().crop_plate(filepath)
        if cropped_plate is None:
            return jsonify({'error': 'No license plate detected'}), 400

        result = recognizer().detect_text(np.array(cropped_plate))
        cleaned_texts = recognizer().clean_text(result[1])

        car = Car(resident_id=resident_id, license_plate=cleaned_texts[0] if cleaned_texts else 'PENDING')
        db.session.add(car)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Car added pending verification',
            'car_id': car.id,
            'license_plate': car.license_plate,
            'debug_image': result[2]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

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
        resident.face_image = image_data  # Store the original image

        db.session.commit()
        
        return jsonify({
            'message': 'Face data updated successfully',
            'resident_id': resident_id,
            'has_face_data': True
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating resident face: {str(e)}")
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

@admin_bp.route('/guest/<int:guest_id>/car', methods=['POST'])
@jwt_required()
def add_guest_car(guest_id):
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
        return jsonify({'error': 'Invalid or no file selected'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)

        cropped_plate = recognizer().crop_plate(filepath)
        if cropped_plate is None:
            return jsonify({'error': 'No license plate detected'}), 400

        result = recognizer().detect_text(np.array(cropped_plate))
        cleaned_texts = recognizer().clean_text(result[1])

        # Placeholder for guest car (consider adding a GuestCar model)
        return jsonify({
            'status': 'success',
            'message': 'Car added pending verification',
            'guest_id': guest_id,
            'license_plate': cleaned_texts[0] if cleaned_texts else 'PENDING',
            'debug_image': result[2]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

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