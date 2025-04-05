from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import numpy as np
from app.models.user import User, UserRole, Resident
from app.extensions import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/residents', methods=['GET'])
@jwt_required()
def get_all_residents():
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role != UserRole.ADMIN:
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

@admin_bp.route('/resident/<int:resident_id>/face', methods=['POST'])
@jwt_required()
def update_resident_face(resident_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role != UserRole.ADMIN:
            return jsonify({'error': 'Unauthorized'}), 403

        resident = Resident.query.get(resident_id)
        if not resident:
            return jsonify({'error': 'Resident not found'}), 404

        if 'face_data' not in request.files:
            return jsonify({'error': 'No face data provided'}), 400

        face_data = request.files['face_data'].read()
        resident.face_data_ref = face_data
        db.session.commit()

        return jsonify({
            'message': 'Face data updated successfully',
            'resident_id': resident_id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500