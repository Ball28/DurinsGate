from datetime import datetime
from models import db


class FileAssignment(db.Model):
    """Many-to-many relationship between users and files"""
    __tablename__ = 'file_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False, index=True)
    
    # Assignment metadata
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expiration_date = db.Column(db.DateTime)  # Optional expiration
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], back_populates='assigned_files')
    file = db.relationship('File', foreign_keys=[file_id], back_populates='assigned_to_users')
    assigned_by = db.relationship('User', foreign_keys=[assigned_by_id])
    
    # Composite index for efficient queries
    __table_args__ = (
        db.Index('idx_user_file', 'user_id', 'file_id'),
    )
    
    def is_expired(self):
        """Check if this assignment has expired"""
        if not self.expiration_date:
            return False
        return datetime.utcnow() > self.expiration_date
    
    def __repr__(self):
        return f'<FileAssignment user_id={self.user_id} file_id={self.file_id}>'
