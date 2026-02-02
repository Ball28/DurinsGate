"""Admin decorators for access control and audit logging"""
from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user
from datetime import datetime
from models import db


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.is_admin():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('customer.dashboard'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def audit_log(action_type):
    """Decorator to log admin actions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Execute the function
            result = f(*args, **kwargs)
            
            # Log the action (in a real app, you'd have an AuditLog model)
            # For now, we'll just print it
            if current_user.is_authenticated:
                log_entry = {
                    'timestamp': datetime.utcnow(),
                    'user_id': current_user.id,
                    'username': current_user.username,
                    'action': action_type,
                    'endpoint': request.endpoint,
                    'ip_address': request.remote_addr
                }
                # In production, save this to database
                print(f"AUDIT LOG: {log_entry}")
            
            return result
        
        return decorated_function
    
    return decorator
