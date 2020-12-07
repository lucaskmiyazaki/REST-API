from flask import Flask
from flask import request, jsonify, make_response
import json

# Elastic Beanstalk looks for an 'application' that is callable by default
app = Flask(__name__)

# model
class Users:
    def __init__(self):
        self.db = [{"id": 0, "username": "lucas", "email": "example@email.com", "password": "9298976"}]
        self.col = ['username', 'email', 'password']
        self.n_user = 1

    def user_validation(self, user):
        if type(user) != dict:
            return False
        if not (all(key in self.col for key in user.keys()) and all(key in user.keys() for key in self.col)):
            return False
        return True
    
    def password_validation(self, user):
        if 'username' in user.keys() and 'password' in user.keys():
            for i in range(len(self.db)):
                if self.db[i]['username'] == user['username'] and self.db[i]['password'] == user['password']:
                    return True
        return False

    def create(self, user, nid=None):
        if nid == None:
            nid = self.n_user
            self.n_user += 1

        if not self.user_validation(user):
            return False, "invalid JSON" 

        user['id'] = nid
        self.db.append(user)
        return True, user

    def find(self, nid):
        for i in range(len(self.db)):
            if self.db[i]['id'] == nid:
                user = self.db[i]
                index = i
                return user, index
        return None, None

    def read(self, nid=None):
        if nid == None:
            data = {"users": self.db}
            return True, data 

        user, index = self.find(nid)

        if not user:
            return False, "id not found" 

        return True, user 

    def delete(self, nid):
        user, index = self.find(nid)

        if not user:
            return False, "id not found" 

        self.db.pop(index)
        return True, user #data, 200

    def update(self, user, nid):
        success, content = self.delete(nid)
        if success:
            return self.create(user, nid)
        else: return content

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

    if password_validation(content):
        return jsonify({"login": True}), 200
    else: return jsonify({"login": False}), 200

  
# Run the application
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production application.
    app.debug = True
    app.run(host="0.0.0.0", debug=True)
