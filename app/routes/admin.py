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

admin_bp = Blueprint('admin', __name__)

# Use global models via current_app
facial_recognition = lambda: current_app.facial_recognition
recognizer = lambda: current_app.recognizer

@admin_bp.route('/dashboard')
@jwt_required()
def dashboard():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != 'ADMIN':
            return redirect(url_for('auth.login'))
        return render_template('admin/dashboard.html', user=current_user)
    except Exception as e:
        return redirect(url_for('auth.login'))

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 403
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users]
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
                'name': r.user.name,
                'email': r.user.email,
                'has_face_data': r.face_data_ref is not None,
                'homes': [{
                    'section': h.home_section,
                    'number': h.home_num,
                    'apartment': h.home_appart
                } for h in r.homes],
                'cars': [{
                    'license_plate': c.license_plate
                } for c in r.cars]
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
    
    image_data = file.read()
    try:
        embedding = facial_recognition().generate_embedding(image_data)
        resident.face_data_ref = pickle.dumps(embedding)  # Match your Guest model’s pickle usage
        db.session.commit()
        return jsonify({
            'message': 'Face data updated successfully',
            'resident_id': resident_id
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/resident/<int:resident_id>/guest', methods=['POST'])
@jwt_required()
def add_guest_to_resident(resident_id):
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 403

    resident = Resident.query.get(resident_id)
    if not resident:
        return jsonify({'error': 'Resident not found'}), 404

    try:
        name = request.form.get('name')
        if not name:
            return jsonify({'error': 'Name is required'}), 400

        end_date_str = request.form.get('end_date')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else datetime.now() + timedelta(days=1)

        if 'image' in request.files:
            image_data = request.files['image'].read()
        else:
            return jsonify({'error': 'Image is required'}), 400

        embedding = facial_recognition().generate_embedding(image_data)
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

    image_data = file.read()
    try:
        test_embedding = facial_recognition().generate_embedding(image_data)
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
            current_invitation = best_match.get_current_invitation()
            return jsonify({
                'guest_id': best_match.id,
                'name': best_match.name,
                'distance': float(min_distance),
                'invitation': {
                    'id': current_invitation.id,
                    'status': current_invitation.status.value
                } if current_invitation else None
            }), 200
        return jsonify({'message': 'No match found', 'distance': float(min_distance)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
                'distance': float(min_distance)
            }), 200
        return jsonify({'message': 'No match found', 'distance': float(min_distance)})
    except Exception as e:
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