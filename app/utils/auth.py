from functools import wraps
from flask import redirect, url_for
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except:
            return redirect(url_for('home'))
    return decorated