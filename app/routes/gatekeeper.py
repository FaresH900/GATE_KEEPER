from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

gatekeeper_bp = Blueprint('gatekeeper', __name__)


@gatekeeper_bp.route('/dashboard')
@jwt_required()
def dashboard():
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'GATEKEEPER':
        return redirect(url_for('auth.login'))
    return render_template('gatekeeper/dashboard.html', user=current_user)
