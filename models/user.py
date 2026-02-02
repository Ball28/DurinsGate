from datetime import datetime
from models import db
from flask_login import UserMixin
import bcrypt


class User(UserMixin, db.Model):
    """User model for both customers and administrators"""
    __tablename__ = 'users'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')  # 'admin' or 'customer'
    
    # Profile information
    company_name = db.Column(db.String(200))
    contact_info = db.Column(db.Text)
    
    # Security fields
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_locked = db.Column(db.Boolean, default=False, nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    
    # MFA fields
    mfa_enabled = db.Column(db.Boolean, default=False)
    mfa_secret = db.Column(db.String(32))
    
    # Terms acceptance
    terms_accepted = db.Column(db.Boolean, default=False)
    terms_accepted_date = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_files = db.relationship('FileAssignment', foreign_keys='FileAssignment.user_id', back_populates='user', lazy='dynamic')
    download_logs = db.relationship('DownloadLog', back_populates='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify the user's password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def lock_account(self, duration):
        """Lock the user account for a specified duration"""
        self.is_locked = True
        self.locked_until = datetime.utcnow() + duration
        db.session.commit()
    
    def unlock_account(self):
        """Unlock the user account"""
        self.is_locked = False
        self.locked_until = None
        self.failed_login_attempts = 0
        db.session.commit()
    
    def is_account_locked(self):
        """Check if account is currently locked"""
        if not self.is_locked:
            return False
        
        if self.locked_until and datetime.utcnow() > self.locked_until:
            # Auto-unlock if lockout period has passed
            self.unlock_account()
            return False
        
        return True
    
    def increment_failed_login(self):
        """Increment failed login attempts"""
        self.failed_login_attempts += 1
        db.session.commit()
    
    def reset_failed_login(self):
        """Reset failed login attempts counter"""
        self.failed_login_attempts = 0
        db.session.commit()
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'
