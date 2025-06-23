from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User, UserRole, Resident
from app.extensions import db
import os 
import base64
import logging

resident_bp = Blueprint('resident', __name__)
logger = logging.getLogger(__name__)

# current_user = "not logged in"


@resident_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def render_dashboard():
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'RESIDENT':
        return redirect(url_for('auth.login'))
    debug_dir = os.path.join(current_app.static_folder, 'debug')
    debug_images = [f'/static/debug/{f}' for f in os.listdir(debug_dir) if f.endswith('.jpg')]
    return render_template('resident/dashboard.html', user=current_user, debug_images=debug_images)


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

@resident_bp.route('/resident/<int:resident_id>/guest', methods=['POST'])
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


@resident_bp.route('/test', methods=['GET','POST'])
@jwt_required()
def test():
    current_user = User.query.get(get_jwt_identity())
    logger.info(current_user)
    return jsonify({'current_user': str(current_user)}), 200