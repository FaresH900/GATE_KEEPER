from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import (
    create_access_token, 
    set_access_cookies,
    jwt_required, 
    get_jwt_identity, 
    get_jwt
)
from app.models.user import User, UserRole
from app.models.token import TokenBlocklist
from app.extensions import db, bcrypt
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger('app')

# @auth_bp.route('/login', methods=['GET'])
# def login_page():
#     return render_template('auth/login.html')

# @auth_bp.route('/login', methods=['POST'])
# def login():
#     try:
#         logger.info("Processing login request")
        
#         # Log raw request data
#         logger.info(f"Request data: {request.get_data()}")
#         data = request.get_json()
#         logger.info(f"Parsed JSON data: {data}")
        
#         if not data or not data.get('email') or not data.get('password'):
#             logger.warning("Missing email or password in request")
#             return jsonify({'error': 'Missing email or password'}), 400
        
#         # Log email being checked
#         email = data.get('email')
#         logger.info(f"Attempting login for email: {email}")
        
#         user = User.query.filter_by(email=email).first()
#         if not user:
#             logger.warning(f"No user found with email: {email}")
#             return jsonify({'error': 'Invalid email or password'}), 401
        
#         logger.info(f"Found user: {user.email}, role: {user.role}")
        
#         # Log password check
#         password = data.get('password')
#         password_check = user.check_password(password)
#         logger.info(f"Password check result: {password_check}")
        
#         if not password_check:
#             logger.warning("Invalid password provided")
#             return jsonify({'error': 'Invalid email or password'}), 401
        
#         # Create tokens
#         access_token = create_access_token(identity=str(user.id))
#         # refresh_token = create_refresh_token(identity=str(user.id))
        
#         response_data = {
#             'message': 'Login successful',
#             'access_token': access_token,
#             # 'refresh_token': refresh_token,
#             'user': user.to_dict()
#         }
#         set_access_cookies(response, access_token)  # Set token in cookie
#         logger.info(f"Login successful for user: {user.email}")
#         logger.info(f"Response data: {response_data}")
        
#         return jsonify(response_data), 200
        
#     except Exception as e:
#         logger.error(f"Login error: {str(e)}", exc_info=True)
#         return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        logger.info("Serving login page")
        return render_template('auth/login.html')

    logger.info("Processing login request")
    logger.info(f"Raw request data: {request.data}")
    logger.info(f"Content-Type header: {request.headers.get('Content-Type')}")
    try:
        data = request.get_json()
        logger.info(f"Parsed request data: {data}")
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Invalid JSON payload'}), 400

    if not data or 'email' not in data or 'password' not in data:
        logger.error("Missing email or password in request")
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        logger.info(f"Invalid credentials for email: {data['email']}")
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=str(user.id))
    response = jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    })
    set_access_cookies(response, access_token)
    logger.info(f"Login successful for user: {user.email}")
    return response, 200


@auth_bp.route('/check_token', methods=['GET'])
@jwt_required()
def check_token():
    try:
        logger.info("/check_token send")
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({
            'valid': True,
            'user': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 401

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({'message': 'Logout successful'})
    response.delete_cookie('access_token_cookie')
    response.delete_cookie('csrf_access_token')
    return response, 200
    # try:
    #     jti = get_jwt()['jti']
    #     user_id = int(get_jwt_identity())
        
    #     token_block = TokenBlocklist(jti=jti, user_id=user_id)
    #     db.session.add(token_block)
    #     db.session.commit()
        
    #     return jsonify({'message': 'Successfully logged out'}), 200
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        return jsonify({'access_token': access_token}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/test_auth', methods=['POST'])
def test_auth():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            })
            
        password_check = user.check_password(password)
        
        return jsonify({
            'status': 'success',
            'email': email,
            'stored_hash': user.password_hash,
            'password_check': password_check
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })