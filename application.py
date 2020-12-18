from flask import Flask
from flask import request, jsonify, make_response
import json
from model.users import Users
from encrypt import EncryptionManager

# Elastic Beanstalk looks for an 'application' that is callable by default
app = Flask(__name__)


# helper functions
def error_message(message):
    if type(message) != str:
        message = "error"
        code = 400
    elif message == "invalid JSON":
        code = 400
    elif message == "id not found":
        code = 404
    return jsonify({"error_message": message}), code

users_db = Users()
manager = EncryptionManager()

# Flask endpoints
@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/healthcheck')
def health_check():
    return jsonify({"alive": True})

@app.route('/users', methods=['POST', 'GET'])
def users():
    if request.method == 'POST':
        user = request.json
        success, content = users_db.create(user)
        if success: return jsonify(content), 200
        else: return error_message(content)

    if request.method == 'GET':
        success, content = users_db.read()
        if success: return jsonify(content), 200
        else: return error_message(content)

@app.route('/users/<nid>', methods=['GET', 'PUT', 'DELETE'])
def user(nid):
    nid = int(nid)
    if request.method == 'GET':
        success, content = users_db.read(nid)
        if success: return jsonify(content), 200
        else: return error_message(content)
        
    if request.method == 'PUT':
        new_user = request.json
        success, content = users_db.update(new_user, nid)
        if success: return jsonify(content), 200
        else: return error_message(content)

    if request.method == 'DELETE':
        success, content = users_db.delete(nid)
        if success: return jsonify({"success": True}), 200
        else: return error_message(content)

@app.route('/login', methods=['POST'])
def login():
    content = request.json

    if users_db.password_validation(content):
        return jsonify({"login": True}), 200
    else: return jsonify({"login": False}), 200

@app.route('/fakelogin', methods=['POST'])
def fake_login():
    if request.method == 'POST':
        content = request.json
        success, user = users_db.password_validation(content)
        if success:
            resp = make_response(jsonify({"login": True}), 200)
            secret_id = manager.updateEncryptor(str(user['id'])) 
            manager.finalizeEncryptor()
            resp.set_cookie('user_id', secret_id)
            return resp
        else: return jsonify({"login": False}), 200

@app.route('/welcome', methods=['GET'])
def welcome():
    secret_id = request.cookies.get('user_id')
    if secret_id != None:
        nid = manager.updateDecryptor(secret_id)
        manager.finalizeDecryptor()
        nid = int(nid)
        success, user = users_db.read(nid)
        if success: return "Hello %s"%user['username']
        else: return "user deleted"
    else:
        return "please log in first"

@app.route('/logout', methods=['DELETE'])
def logout():
    resp = make_response(jsonify({"logout": True}), 200)
    resp.set_cookie('user_id', '', max_age=0)
    return resp


  
# Run the application
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production application.
    app.debug = True
    app.run(host="0.0.0.0", debug=True)
