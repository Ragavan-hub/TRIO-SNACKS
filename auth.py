"""
Authentication utilities for the Snacks Shop application
"""
from functools import wraps
from flask import session, redirect, url_for, request
from models import User

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role for routes"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if not user or not user.is_admin():
                return redirect(url_for('billing'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get the current logged-in user"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

