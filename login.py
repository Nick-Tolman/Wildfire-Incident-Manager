from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Dummy user data for authentication
users = {
    "john_doe": "password123",
    "jane_doe": "securepassword",
}

@app.route('/auth/login', methods=['POST'])
def authenticate():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username or password is missing'}), 400

    if username not in users:
        return jsonify({'message': 'Invalid username'}), 401

    if users[username] != password:
        return jsonify({'message': 'Incorrect password'}), 401

    return jsonify({'message': 'Login successful'}), 200

if __name__ == '__main__':
    app.run(port=5971, debug=True)
