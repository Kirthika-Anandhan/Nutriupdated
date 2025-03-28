from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd
import json
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import logging
from bson import ObjectId

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# Configure Google Generative AI
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["myDatabase"]
users_collection = db["Users"]

try:
    db.list_collection_names()  # ✅ FIXED: Use db.list_collection_names() instead of mongo.db
    print("✅ MongoDB Connected Successfully!")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")

def create_pdf_report(data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Times-Italic", 24)
    c.drawString(50, height - 50, "Health Report")

    # Add timestamp
    c.setFont("Times-Italic", 12)
    c.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Add health metrics if available
    y_position = height - 100
    c.setFont("Times-Italic", 14)

    if 'file' in data:
        c.drawString(50, y_position, "File Analysis Report")
        y_position -= 30
        c.setFont("Times-Italic", 12)
        c.drawString(50, y_position, f"Analyzed file: {data['file']}")
        y_position -= 20

    if 'health_metrics' in data:
        metrics = data['health_metrics']
        y_position -= 30
        c.setFont("Times-Italic", 14)
        c.drawString(50, y_position, "Health Metrics")
        y_position -= 20
        c.setFont("Times-Italic", 12)
        for key, value in metrics.items():
            c.drawString(50, y_position, f"{key}: {value}")
            y_position -= 20

    # Recommendations
    y_position -= 30
    c.setFont("Times-Italic", 14)
    c.drawString(50, y_position, "Recommendations")
    y_position -= 20

    c.setFont("Times-Italic", 12)
    recommendations = [
        "Maintain a balanced diet with proper nutrition",
        "Exercise regularly for at least 30 minutes daily",
        "Get adequate sleep (7-9 hours per night)",
        "Stay hydrated by drinking enough water",
        "Practice stress management techniques"
    ]
    for rec in recommendations:
        c.drawString(50, y_position, f"• {rec}")
        y_position -= 20

    # Footer
    c.setFont("Times-Italic", 10)
    c.drawString(50, 30, "This report is generated by NutriFlow Health System")

    c.save()
    buffer.seek(0)
    return buffer

def generate_personalized_report(data):
    prompt = f"""
    Given the following health report data, generate a detailed personalized health recommendation:
    {data}
    The report should include key insights, improvement suggestions, and health risk analysis.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
        return response.text if response and response.text else "AI response was empty."
    except Exception as e:
        return f"Error generating AI report: {str(e)}"

@app.route('/generate-report-from-file', methods=['POST'])
def generate_report_from_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # ✅ FIXED: Read file once
        file_content = file.read()

        report_data = {
            'file': file.filename,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'health_metrics': {
                'File Type': file.content_type,
                'File Size': f"{len(file_content)} bytes"
            }
        }

        # Generate PDF
        pdf_buffer = create_pdf_report(report_data)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='health_report.pdf'
        )
    except Exception as e:
        logging.error(f"Error generating report from file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate-report', methods=['POST'])
def generate_report():
    try:
        # Fetch latest data from MongoDB
        latest_data = users_collection.find_one(sort=[("_id", -1)])
        if not latest_data:
            return jsonify({"message": "No user data found!"}), 404

        # Convert ObjectId to string
        latest_data['_id'] = str(latest_data['_id'])
        
        # Add health metrics
        latest_data['health_metrics'] = {
            'BMI': '24.5',
            'Blood Pressure': '120/80',
            'Heart Rate': '72 bpm',
            'Sleep Quality': 'Good',
            'Activity Level': 'Moderate'
        }

        # Generate PDF
        pdf_buffer = create_pdf_report(latest_data)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='health_report.pdf'
        )
    except Exception as e:
        logging.error(f"Error generating report: {e}")
        return jsonify({'error': str(e)}), 500

# Home route (renders frontend form)
@app.route("/")
def index():
    return render_template("details.html")

# Signup Route
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    full_name = data.get("fullName")
    age = data.get("age")
    gender = data.get("gender")
    email = data.get("email")
    phone_number = data.get("phoneNumber")
    password = data.get("password")

    if users_collection.find_one({"email": email}):
        return jsonify({"message": "Email already exists"}), 400

    hashed_password = generate_password_hash(password)
    users_collection.insert_one({
        "fullName": full_name,
        "age": age,
        "gender": gender,
        "email": email,
        "phoneNumber": phone_number,
        "password": hashed_password
    })

    return jsonify({"message": "Signup successful"}), 201

# Login Route
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    user = users_collection.find_one({"email": email})
    
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid email or password"}), 401
    
    return jsonify({"message": "Login successful"}), 200

# Upload CSV/JSON and Generate Report
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
            data = df.to_dict(orient='records')
        elif file.filename.endswith('.json'):
            data = json.load(file.stream)
        else:
            return jsonify({"error": "Invalid file format. Upload CSV or JSON only."}), 400

        report = generate_personalized_report(data)
        return jsonify({"personalized_report": report})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#data collection
@app.route("/submit", methods=["POST"])
def submit():
    try:
        data = request.json
        if not data:
            return jsonify({"message": "No data received"}), 400  # Handle empty request

        # Validate required fields
        required_fields = ["name", "age", "weight", "height", "blood_pressure", "cholesterol", "sugar_level"]
        for field in required_fields:
            if field not in data or not data[field]:  # Check missing/empty fields
                return jsonify({"message": f"Missing or empty field: {field}"}), 400

        # Insert data into MongoDB
        users_collection.insert_one(data)

        return jsonify({"message": "Data submitted successfully!"}), 201  # HTTP 201 for created
    except Exception as e:
        print("Error:", e)  # Log error
        return jsonify({"message": "Internal Server Error"}), 500

# ✅ Chatbot Route

# Configure Gemini API (Make sure you have set up the API key)
genai.configure(api_key="AIzaSyBiudb7oc_VXiP_8iJal7mSCnMimBwzfd4")

def get_medical_response(user_message):
    """Fetches a short medical response from Gemini AI"""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        
        # Use a system prompt to make responses short and medically focused
        prompt = f"""
        You are a medical assistant. Provide a *short, medically accurate* response to the following query.
        Avoid unnecessary conversational elements. Respond in *1-2 sentences max*.
        
        *User Query:* {user_message}
        """

        response = model.generate_content(prompt)

        # Extract response text and ensure it's concise
        reply = response.text.strip() if response.text else "I'm unable to provide an answer at the moment."
        return reply[:150]  # Ensure the response is short
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/chat", methods=["POST"])
def chat():
    """Handles user messages and returns a short medical response"""
    user_message = request.json.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please enter a valid message!"})

    reply = get_medical_response(user_message)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True, port=5000) 