from flask import Flask
from flask import request, jsonify, make_response
import json
import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend

# Elastic Beanstalk looks for an 'application' that is callable by default
app = Flask(__name__)

# model
class Users:
    def __init__(self):
        self.db = []
        self.col = ['username', 'email', 'password']
        self.n_user = 0
        self.salt = os.urandom(16)
        _success, _user = self.create({"username": "lucas", "email": "example@email.com", "password": "9298976"})

    def user_validation(self, user):
        if type(user) != dict:
            return False
        if not (all(key in self.col for key in user.keys()) and all(key in user.keys() for key in self.col)):
            return False
        if user['username'] in [u['username'] for u in self.db]:
            return False
        if type(user['password']) != str:
            return False
        return True
    
    def password_validation(self, user):
        if 'username' in user.keys() and 'password' in user.keys():
            for i in range(len(self.db)):
                if self.db[i]['username'] == user['username']:
                    kdf = Scrypt(salt=self.salt, length=32, n=2**14, r=8, p=1, backend=default_backend())
                    try:
                        kdf.verify(user['password'].encode(), self.db[i]['password_digest'])
                        return True, self.db[i]
                    except:
                        pass
        return False, None

    def filter_query(self, data):
        if 'users' in data.keys():
            users = []
            for user in data['users']:
                users.append(self.filter_query(user))
            return {'users': users}
        else: user = data

        response = {}
        for key in user:
            if key != 'password_digest':
                response[key] = user[key]
        return response

    def create(self, user, nid=None):
        if nid == None:
            nid = self.n_user
            self.n_user += 1

        if not self.user_validation(user):
            return False, "invalid JSON" 

        new_user = {}
        new_user['id'] = nid
        new_user['username'] = user['username']
        new_user['email'] = user['email']

        kdf = Scrypt(salt=self.salt, length=32, n=2**14, r=8, p=1, backend=default_backend())
        new_user['password_digest'] = kdf.derive(user['password'].encode())

        self.db.append(new_user)
        return True, self.filter_query(new_user)

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
            return True, self.filter_query(data) 

        user, index = self.find(nid)

        if not user:
            return False, "id not found" 

        return True, self.filter_query(user) 

    def delete(self, nid):
        user, index = self.find(nid)

        if not user:
            return False, "id not found" 

        self.db.pop(index)
        return True, user

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
            resp.set_cookie('user_id', str(user['id']).encode())
            return resp
        else: return jsonify({"login": False}), 200

@app.route('/welcome', methods=['GET'])
def welcome():
    nid = request.cookies.get('user_id')
    if nid != None:
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
