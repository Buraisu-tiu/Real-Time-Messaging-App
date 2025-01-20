from flask import *
from firebase_admin import auth
import jwt
from config import db
from config import Config
import firestore
import firebase_admin


routes = Blueprint('routes', __name__)

@routes.route("/verify-token", methods=["POST"])
def verify_token():
    token = request.json.get("token")
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token["uid"]
        # Generate JWT for the session
        jwt_token = jwt.encode({"uid": uid}, Config.SECRET_KEY, algorithm="HS256")
        return jsonify({"jwt": jwt_token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@routes.route("/log-session", methods=["POST"])
def log_session():
    data = request.json
    token = request.headers.get("Authorization").split("Bearer ")[-1]
    try:
        decoded_jwt = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        uid = decoded_jwt["uid"]

        # Add log to Firestore
        db.collection("study_logs").add({
            "user_id": uid,
            "duration": data["duration"],
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        return jsonify({"message": "Session logged successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@routes.route("/leaderboard", methods=["GET"])
def leaderboard():
    try:
        # Fetch all study logs from Firestore
        users = {}
        logs = db.collection("study_logs").stream()
        for log in logs:
            data = log.to_dict()
            user_id = data.get("user_id")
            duration = data.get("duration", 0)
            users[user_id] = users.get(user_id, 0) + duration

        # Sort users by total study time in descending order
        ranked_users = sorted(users.items(), key=lambda x: x[1], reverse=True)
        return jsonify({"leaderboard": ranked_users}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route("/register", methods=["POST"])
def register():
    email = request.json.get("email")
    password = request.json.get("password")

    try:
        user = auth.create_user(email=email, password=password)
        return jsonify({"message": "User  created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@routes.route("/", methods=["GET"])
def index():
    if "user" not in session:  # Check if the user is logged in
        return redirect(url_for("routes.register_page"))  # Redirect to registration page
    return render_template("index.html")  # Render the home page for logged-in users

# Add these routes to your existing routes.py file
@routes.route("/login", methods=["GET"])
def login():
    return render_template("login.html")  # Render the login.html template

@routes.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")  # Render the register.html template

@routes.route("/login", methods=["POST"])
def login_submit():
    email = request.form.get("email")
    password = request.form.get("password")
    try:
        # Authenticate with Firebase
        user = firebase_admin.auth.get_user_by_email(email)
        session["user"] = user.uid  # Store user ID in session
        return redirect(url_for("routes.index"))  # Redirect to home page
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@routes.route("/register", methods=["POST"])
def register_submit():
    print("Request Content-Type:", request.content_type)  # Debug: Check Content-Type
    print("Request Data:", request.form)  # Debug: Check form data

    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")  # Use underscore to match form data

    if not email or not password or not confirm_password:
        return jsonify({"error": "Missing required fields"}), 400

    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    try:
        # Create user in Firebase
        user = auth.create_user(email=email, password=password)
        session["user"] = user.uid  # Store user ID in session
        return jsonify({"message": "Registration successful"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
def login_required(f):
    def wrapper(*args, **kwargs):
        if "user" not in session:  # Check if the user is logged in
            return redirect(url_for("routes.register_page"))  # Redirect to registration page
        return f(*args, **kwargs)
    return wrapper

@routes.route("/logout", methods=["GET"])
def logout():
    session.pop("user", None)  # Clear the session
    return redirect(url_for("routes.register_page"))  # Redirect to registration page