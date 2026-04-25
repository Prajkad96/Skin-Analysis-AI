from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from extensions import db  # Import db from extensions.py
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import base64
import uuid
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.preprocessing import image
import traceback
import json
from sqlalchemy.sql import func

# Flask setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Initialize db with the app
db.init_app(app)
from models import Consultation,Progress
model = MobileNetV2(weights="imagenet")  

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        """Hash the password and set it to the password_hash field"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hashed password"""
        return check_password_hash(self.password_hash, password)

# class Consultation(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(100), nullable=False)
#     date = db.Column(db.Date, nullable=False)
#     message = db.Column(db.Text, nullable=True)
#     def __repr__(self):
#         return f'<Consultation {self.id}>'

def analyze_skin_image(image_path):
    try:
        # Load and preprocess the image
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        # Get predictions from MobileNetV2
        predictions = model.predict(img_array)
        
        # Mock detection scores for specific conditions
        # In a real implementation, you'd use a specialized model for each condition
        mock_scores = {
            "acne": np.random.uniform(0.3, 0.8),
            "eczema": np.random.uniform(0.2, 0.7),
            "psoriasis": np.random.uniform(0.1, 0.6),
            "hyperpigmentation": np.random.uniform(0.2, 0.8),
            "wrinkles": np.random.uniform(0.3, 0.7),
            "eyebags": np.random.uniform(0.2, 0.6)
        }

        # Determine skin type based on image analysis
        skin_types = ["Oily", "Dry", "Combination", "Normal", "Sensitive"]
        skin_type = np.random.choice(skin_types, p=[0.25, 0.25, 0.2, 0.2, 0.1])

        # Generate severity levels
        def get_severity(score):
            if score < 0.3: return "Mild"
            elif score < 0.6: return "Moderate"
            else: return "Severe"

        # Structure the analysis results
        skin_analysis = {
            "skin_type": {
                "type": skin_type,
                "confidence": float(np.random.uniform(0.7, 0.9))
            },
            "conditions": {
                condition: {
                    "detected": score > 0.3,
                    "severity": get_severity(score),
                    "confidence": float(score),
                    "affected_areas": ["T-zone", "Cheeks", "Forehead"] if score > 0.3 else []
                } for condition, score in mock_scores.items()
            },
            "recommendations": {
                "skincare_routine": {
                    "morning": [
                        "Gentle cleanser",
                        "Toner",
                        "Vitamin C serum",
                        "Moisturizer",
                        "Sunscreen (SPF 30+)"
                    ],
                    "evening": [
                        "Oil-based cleanser",
                        "Water-based cleanser",
                        "Treatment serum",
                        "Moisturizer",
                        "Night cream"
                    ]
                },
                "products": {
                    "cleanser": get_product_recommendation(skin_type, "cleanser"),
                    "moisturizer": get_product_recommendation(skin_type, "moisturizer"),
                    "treatment": get_product_recommendation(skin_type, "treatment"),
                    "sunscreen": get_product_recommendation(skin_type, "sunscreen")
                },
                "lifestyle": [
                    "Stay hydrated - drink at least 8 glasses of water daily",
                    "Get 7-8 hours of sleep",
                    "Protect skin from sun exposure",
                    "Maintain a balanced diet rich in antioxidants"
                ]
            }
        }

        return skin_analysis

    except Exception as e:
        print(f"Error in analyze_skin_image: {str(e)}")
        return {
            "error": str(e),
            "skin_type": {"type": "Unknown", "confidence": 0},
            "conditions": {},
            "recommendations": {}
        }

def get_product_recommendation(skin_type, product_type):
    """Helper function to get product recommendations based on skin type"""
    recommendations = {
        "Oily": {
            "cleanser": "Salicylic acid cleanser",
            "moisturizer": "Oil-free gel moisturizer",
            "treatment": "Niacinamide serum",
            "sunscreen": "Light, oil-free sunscreen"
        },
        "Dry": {
            "cleanser": "Cream-based gentle cleanser",
            "moisturizer": "Rich, hydrating cream",
            "treatment": "Hyaluronic acid serum",
            "sunscreen": "Moisturizing sunscreen"
        },
        "Combination": {
            "cleanser": "Balanced pH cleanser",
            "moisturizer": "Light-weight lotion",
            "treatment": "BHA/AHA toner",
            "sunscreen": "Dual-action sunscreen"
        },
        "Normal": {
            "cleanser": "Mild foam cleanser",
            "moisturizer": "Balance moisturizer",
            "treatment": "Vitamin C serum",
            "sunscreen": "Daily protection sunscreen"
        },
        "Sensitive": {
            "cleanser": "Fragrance-free gentle cleanser",
            "moisturizer": "Calming moisturizer",
            "treatment": "Centella asiatica serum",
            "sunscreen": "Mineral sunscreen"
        }
    }
    return recommendations.get(skin_type, {}).get(product_type, "Generic recommendation")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):  # Check hashed password
            session['user_id'] = user.id
            session['user_name'] = user.name
            return redirect(url_for('index'))
        
        return render_template('signin.html', error="Invalid email or password")
    
    return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        print(request.form)  # Print the form data for debugging
        
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Check if the email already exists in the database
        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error="Email already exists")
        
        # Check if passwords match
        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match")
        
        # Create a new user with hashed password for security
        new_user = User(name=name, email=email)
        new_user.set_password(password)  # Hash the password before saving
        db.session.add(new_user)
        db.session.commit()
        
        # Log the user in automatically after successful registration
        session['user_id'] = new_user.id
        session['user_name'] = new_user.name
        
        return redirect(url_for('index'))  # Redirect to the homepage

    return render_template('signup.html')

@app.route('/signout')
def signout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/book-consultation', methods=['GET', 'POST'])
def book_consultation():
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        date = request.form['date']
        message = request.form.get('message', '')
        
        consultation = Consultation(
            name=name,
            email=email,
            date=datetime.strptime(date, '%Y-%m-%d'),
            message=message,
            user_id=session.get('user_id')
        )
        db.session.add(consultation)
        db.session.commit()
        return render_template('book_consultation.html', success=True)
    return render_template('book_consultation.html')

# Enhanced skin analysis function
# def analyze_skin_image(image_path):
#     # Mock AI analysis with more comprehensive results
#     return {
#         'skin_type': {
#             'type': 'Combination',
#             'characteristics': [
#                 'Oily T-zone',
#                 'Dry cheeks',
#                 'Normal chin area'
#             ],
#             'confidence': 0.89
#         },
#         'conditions': {
#             'acne': {
#                 'severity': 'Moderate',
#                 'locations': ['Forehead', 'Cheeks'],
#                 'type': 'Inflammatory',
#                 'confidence': 0.85
#             },
#             'hyperpigmentation': {
#                 'severity': 'Mild',
#                 'type': 'Post-inflammatory',
#                 'locations': ['Cheeks'],
#                 'confidence': 0.78
#             },
#             'wrinkles': {
#                 'severity': 'Minimal',
#                 'type': 'Fine lines',
#                 'locations': ['Around eyes'],
#                 'confidence': 0.92
#             },
#             'rosacea': {
#                 'severity': 'Mild',
#                 'type': 'Erythematotelangiectatic',
#                 'locations': ['Nose', 'Cheeks'],
#                 'confidence': 0.75
#             },
#             'dehydration': {
#                 'severity': 'Moderate',
#                 'indicators': ['Fine lines', 'Dull complexion'],
#                 'confidence': 0.88
#             }
#         },
#         'recommendations': {
#             'immediate_actions': [
#                 'Use gentle, non-foaming cleanser',
#                 'Apply broad-spectrum SPF 50 sunscreen',
#                 'Incorporate hyaluronic acid serum'
#             ],
#             'products': [
#                 {
#                     'type': 'Cleanser',
#                     'ingredients': ['Ceramides', 'Glycerin'],
#                     'frequency': 'Twice daily'
#                 },
#                 {
#                     'type': 'Treatment',
#                     'ingredients': ['Niacinamide', 'Salicylic acid'],
#                     'frequency': 'Evening only'
#                 },
#                 {
#                     'type': 'Moisturizer',
#                     'ingredients': ['Hyaluronic acid', 'Peptides'],
#                     'frequency': 'Morning and evening'
#                 }
#             ],
#             'lifestyle': [
#                 'Increase water intake',
#                 'Protect from sun exposure',
#                 'Consider a humidifier'
#             ],
#             'professional_treatments': [
#                 'Chemical peel for hyperpigmentation',
#                 'LED therapy for inflammation'
#             ]
#         },
#         'severity_scores': {
#             'overall': 65,  # Scale of 0-100
#             'inflammation': 45,
#             'dehydration': 60,
#             'barrier_damage': 40,
#             'sun_damage': 35
#         }
#     }

@app.route('/skin-analysis', methods=['GET', 'POST'])
def skin_analysis():
    try:
        if request.method == 'GET':
            return render_template('skin_analysis.html')

        print("Request received:", request.method, request.content_type)

        # Handle JSON-based request (camera images)
        if request.is_json:
            data = request.get_json()
            if not data or 'images' not in data:
                return jsonify({'error': 'No image data received'}), 400

            analysis_results = {}
            image_paths = {}
            
            for position, image_data in data['images'].items():
                if ',' in image_data:
                    image_data = image_data.split(',')[1]
                
                image_bytes = base64.b64decode(image_data)
                filename = f"{uuid.uuid4()}.jpg"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                
                analysis_result = analyze_skin_image(filepath)
                analysis_results[position] = analysis_result
                image_paths[position] = f"/static/uploads/{filename}"

            return jsonify({
                'success': True,
                'redirect': url_for('analysis_results', 
                                  image_paths=json.dumps(image_paths),
                                  analysis=json.dumps(analysis_results))
            })

        # Handle file upload
        elif 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400

            filename = secure_filename(f"{uuid.uuid4()}.{file.filename.rsplit('.', 1)[1].lower()}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            analysis_result = analyze_skin_image(filepath)
            
            return redirect(url_for('analysis_results',
                                  image_paths=json.dumps({'uploaded': f"/static/uploads/{filename}"}),
                                  analysis=json.dumps({'uploaded': analysis_result})))

        return jsonify({'error': 'No valid image received'}), 400

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/analysis-results')
def analysis_results():
    try:
        image_paths = json.loads(request.args.get('image_paths', '{}'))
        analysis = json.loads(request.args.get('analysis', '{}'))
        return render_template('analysis_results.html', 
                             image_paths=image_paths,
                             analysis=analysis)
    except Exception as e:
        print(f"Error in analysis_results route: {str(e)}")
        return render_template('analysis_results.html',
                             image_paths={},
                             analysis={},
                             error="Error loading analysis results")

@app.route('/progress')
def progress():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    
    try:
        # Get all progress entries for the user, ordered by newest first
        progress_entries = Progress.query.filter_by(
            user_id=session['user_id']
        ).order_by(
            Progress.timestamp.desc()
        ).all()
        
        # Calculate improvements if there are multiple entries
        for i in range(len(progress_entries)):
            if i < len(progress_entries) - 1:
                current = progress_entries[i]
                previous = progress_entries[i + 1]
                
                # Initialize improvements list if None
                if not current.improvements:
                    current.improvements = []
                
                # Compare skin scores if they exist
                if current.skin_score and previous.skin_score:
                    improvement = ((current.skin_score - previous.skin_score) / previous.skin_score) * 100
                    current.improvement = round(improvement, 1)
                else:
                    current.improvement = None
        
        return render_template(
            'progress.html',
            progress=progress_entries,
            user_name=session.get('user_name', 'User')
        )
        
    except Exception as e:
        print(f"Error in progress route: {str(e)}")
        # Log the error properly in production
        return render_template(
            'progress.html',
            progress=[],
            error="An error occurred while loading your progress data."
        )

# Update your analyze_skin_image function to save progress
def save_progress(user_id, image_path, analysis_result):
    try:
        # Extract relevant data from analysis result
        skin_type = analysis_result.get('skin_type', {}).get('type', 'Unknown')
        
        # Calculate a basic skin score (customize based on your needs)
        skin_score = calculate_skin_score(analysis_result)
        
        # Extract conditions
        conditions = [
            condition for condition, details in analysis_result.get('conditions', {}).items()
            if details.get('detected', False)
        ]
        
        # Create new progress entry
        progress_entry = Progress(
            user_id=user_id,
            image_path=image_path,
            result='Analysis Complete',
            skin_type=skin_type,
            skin_score=skin_score,
            conditions=conditions,
            improvements=[],  # Will be calculated when viewing progress
            analysis_data=analysis_result
        )
        
        db.session.add(progress_entry)
        db.session.commit()
        
        return True
        
    except Exception as e:
        print(f"Error saving progress: {str(e)}")
        db.session.rollback()
        return False

def calculate_skin_score(analysis_result):
    """
    Calculate a skin health score based on analysis results
    Returns a score from 0-100
    """
    try:
        base_score = 70  # Start with a base score
        
        # Adjust based on condition severities
        for condition, details in analysis_result.get('conditions', {}).items():
            if details.get('detected'):
                severity = details.get('severity', 'Mild').lower()
                if severity == 'severe':
                    base_score -= 15
                elif severity == 'moderate':
                    base_score -= 10
                elif severity == 'mild':
                    base_score -= 5
        
        # Ensure score stays within 0-100 range
        return max(0, min(100, base_score))
        
    except Exception as e:
        print(f"Error calculating skin score: {str(e)}")
        return 70
    
@app.route('/educational-hub')
def educational_hub():
    return render_template('educational_hub.html')

with app.app_context():
    db.create_all()  # This will create all tables defined in your models
    print("Tables created successfully.")
    
if __name__ == '__main__':
    app.run(debug=True)