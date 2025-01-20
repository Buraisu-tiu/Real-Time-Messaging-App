from flask import *
from firebase_admin import auth
import jwt
from config import db  # Import Firestore instance
from config import Config  # Access app configuration if needed
import firestore

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
    return render_template("index.html")