from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import requests

app = Flask(__name__)
CORS(app)

cred = credentials.Certificate("real-time-messaging-db06e-firebase-adminsdk-88zyg-7cc92a555b.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    message = data['message']
    db.collection('messages').add({'message': message})
    return jsonify({'message': 'Message sent successfully'})

@app.route('/get_messages', methods=['GET'])
def get_messages():
    messages = db.collection('messages').stream()
    messages_list = []
    for message in messages:
        messages_list.append(message.to_dict())
    return jsonify(messages_list)

@app.route('/', methods=['GET'])
def index():
    return 'Welcome to the Real-Time Messaging App!'

if __name__ == '__main__':
    app.run(debug=True)