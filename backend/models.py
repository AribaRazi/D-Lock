# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime

# db = SQLAlchemy()

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password_hash = db.Column(db.String(200), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
#     files = db.relationship('FileMetadata', backref='owner', lazy=True)
    
# class FileMetadata(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     file_hash = db.Column(db.String(64), unique=True, nullable=False)
#     file_name = db.Column(db.String(255), nullable=False)
#     file_size = db.Column(db.Integer, nullable=False)
#     content_type = db.Column(db.String(100))
#     encrypted_filename = db.Column(db.String(255), nullable=False)
#     decryption_key_encrypted = db.Column(db.Text, nullable=False)  # Encrypted with user's key
#     tx_hash = db.Column(db.String(66), nullable=False)
#     upload_date = db.Column(db.DateTime, default=datetime.utcnow)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class FileMetadata(db.Model):
    __tablename__ = 'file_metadata'
    
    id = db.Column(db.Integer, primary_key=True)
    file_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    content_type = db.Column(db.String(100))
    encrypted_filename = db.Column(db.String(255), nullable=False)
    decryption_key_encrypted = db.Column(db.Text, nullable=False)
    tx_hash = db.Column(db.String(100), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, default=1)  # Simplified for now