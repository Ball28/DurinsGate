from datetime import datetime
from models import db


class DownloadLog(db.Model):
    """Audit log for file downloads"""
    __tablename__ = 'download_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False, index=True)
    
    # Download details
    download_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    user_agent = db.Column(db.String(500))
    success = db.Column(db.Boolean, default=True, nullable=False)
    error_message = db.Column(db.String(500))
    
    # Relationships
    user = db.relationship('User', back_populates='download_logs')
    file = db.relationship('File', back_populates='download_logs')
    
    # Composite index for efficient queries
    __table_args__ = (
        db.Index('idx_user_date', 'user_id', 'download_date'),
        db.Index('idx_file_date', 'file_id', 'download_date'),
    )
    
    def __repr__(self):
        return f'<DownloadLog user_id={self.user_id} file_id={self.file_id} date={self.download_date}>'
