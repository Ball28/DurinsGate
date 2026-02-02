from datetime import datetime, timedelta
from models import db
import jwt
from flask import current_app
import os


class File(db.Model):
    """File model for storing uploaded manuals and documents"""
    __tablename__ = 'files'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # Stored filename (unique)
    original_filename = db.Column(db.String(255), nullable=False)  # Original upload name
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)  # Size in bytes
    file_type = db.Column(db.String(50), nullable=False)  # Extension
    
    # Categorization
    category = db.Column(db.String(100))  # e.g., "User Manual", "Technical Specification"
    product_type = db.Column(db.String(100))  # e.g., "Pump Model X", "Valve Series Y"
    version = db.Column(db.String(50))  # e.g., "v2.1", "Rev C"
    description = db.Column(db.Text)
    
    # Metadata
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    uploaded_by = db.relationship('User', foreign_keys=[uploaded_by_id])
    assigned_to_users = db.relationship('FileAssignment', back_populates='file', lazy='dynamic')
    download_logs = db.relationship('DownloadLog', back_populates='file', lazy='dynamic')
    
    def get_download_token(self, user_id):
        """Generate a time-limited download token for this file"""
        expiration = datetime.utcnow() + current_app.config['DOWNLOAD_TOKEN_EXPIRATION']
        
        payload = {
            'file_id': self.id,
            'user_id': user_id,
            'exp': expiration,
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        return token
    
    @staticmethod
    def verify_download_token(token):
        """Verify and decode a download token"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None  # Token expired
        except jwt.InvalidTokenError:
            return None  # Invalid token
    
    def get_file_size_formatted(self):
        """Return human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    
    def is_assigned_to_user(self, user_id):
        """Check if this file is assigned to a specific user"""
        from models.file_assignment import FileAssignment
        assignment = FileAssignment.query.filter_by(
            file_id=self.id,
            user_id=user_id,
            is_active=True
        ).first()
        
        if not assignment:
            return False
        
        # Check expiration date if set
        if assignment.expiration_date and datetime.utcnow() > assignment.expiration_date:
            return False
        
        return True
    
    def __repr__(self):
        return f'<File {self.original_filename}>'
