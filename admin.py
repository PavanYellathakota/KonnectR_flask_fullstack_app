#admin.py 
from functools import wraps
from flask import session, redirect, url_for, flash

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in and is admin
        if 'user_id' not in session or session.get('user_type') != 'Admin':
            flash('Admin access required', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def is_admin(user_type: str) -> bool:
    return user_type.lower() == 'admin'

