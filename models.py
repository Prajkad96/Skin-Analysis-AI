
from sqlalchemy import JSON
from extensions import db
import json
from sqlalchemy.sql import func

class Consultation(db.Model):
    __tablename__ = 'consultation'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)  # Change to DateTime if storing proper dates
    message = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, nullable=False)  # Ensure this exists if you are inserting a user_id

    def __repr__(self):
        return f"<Consultation {self.id}, {self.name}, {self.email}, {self.date}>"


class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    result = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=func.now())
    
    # New fields for enhanced tracking
    skin_type = db.Column(db.String(50))
    skin_score = db.Column(db.Float)
    conditions = db.Column(JSON)  # Store detected conditions as JSON
    improvements = db.Column(JSON)  # Store improvements as JSON
    analysis_data = db.Column(JSON)
    
    user = db.relationship('User', back_populates='progress')