"""Utility functions for file handling"""
import os
import secrets
from werkzeug.utils import secure_filename
from flask import current_app
from datetime import datetime


def allowed_file(filename):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']


def generate_unique_filename(original_filename):
    """Generate a unique filename while preserving extension"""
    # Get file extension
    if '.' in original_filename:
        ext = original_filename.rsplit('.', 1)[1].lower()
    else:
        ext = ''
    
    # Generate unique name with timestamp and random string
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    random_str = secrets.token_hex(8)
    
    if ext:
        return f"{timestamp}_{random_str}.{ext}"
    else:
        return f"{timestamp}_{random_str}"


def get_file_category_path(category):
    """Get the directory path for a file category"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    if category:
        # Sanitize category name for use as directory
        safe_category = secure_filename(category.replace(' ', '_'))
        category_path = os.path.join(upload_folder, safe_category)
    else:
        category_path = os.path.join(upload_folder, 'uncategorized')
    
    # Create directory if it doesn't exist
    os.makedirs(category_path, exist_ok=True)
    
    return category_path


def save_uploaded_file(file, category=None):
    """
    Save an uploaded file securely
    
    Returns: (success, filename, filepath, error_message)
    """
    if not file:
        return False, None, None, "No file provided"
    
    if file.filename == '':
        return False, None, None, "No file selected"
    
    if not allowed_file(file.filename):
        allowed = ', '.join(current_app.config['ALLOWED_EXTENSIONS'])
        return False, None, None, f"File type not allowed. Allowed types: {allowed}"
    
    try:
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename)
        
        # Get category path
        category_path = get_file_category_path(category)
        
        # Full file path
        filepath = os.path.join(category_path, unique_filename)
        
        # Save file
        file.save(filepath)
        
        return True, unique_filename, filepath, None
    
    except Exception as e:
        return False, None, None, f"Error saving file: {str(e)}"


def delete_file(filepath):
    """
    Delete a file from the filesystem
    
    Returns: (success, error_message)
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True, None
        else:
            return False, "File not found"
    except Exception as e:
        return False, f"Error deleting file: {str(e)}"


def get_file_size(filepath):
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath)
    except:
        return 0


def format_file_size(size_bytes):
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def ensure_upload_directory():
    """Ensure the upload directory exists"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
