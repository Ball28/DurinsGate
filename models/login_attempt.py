from datetime import datetime
from models import db


class LoginAttempt(db.Model):
    """Log of all login attempts for security monitoring"""
    __tablename__ = 'login_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(500))
    
    # Attempt details
    success = db.Column(db.Boolean, nullable=False, index=True)
    failure_reason = db.Column(db.String(200))  # e.g., "Invalid password", "Account locked"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Composite index for efficient queries
    __table_args__ = (
        db.Index('idx_username_timestamp', 'username', 'timestamp'),
        db.Index('idx_ip_timestamp', 'ip_address', 'timestamp'),
    )
    
    def __repr__(self):
        return f'<LoginAttempt {self.username} success={self.success} at={self.timestamp}>'
