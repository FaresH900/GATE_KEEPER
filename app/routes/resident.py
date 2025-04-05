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