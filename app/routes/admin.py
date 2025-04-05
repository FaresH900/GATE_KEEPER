from flask import Blueprint, request, jsonify, render_template
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
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'role']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Check if email already exists
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
        
        return jsonify({
            'message': 'User created successfully',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500