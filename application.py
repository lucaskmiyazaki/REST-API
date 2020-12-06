from flask import Flask
from flask import request, jsonify, make_response
import json

# Elastic Beanstalk looks for an 'application' that is callable by default
app = Flask(__name__)

db = [{"id": 0, "username": "lucas", "email": "example@email.com", "password": "9298976"}]
col = ['username', 'email', 'password']
n_user = 1

def user_validation(user):
    if type(user) != dict:
        return False
    if not (all(key in col for key in user.keys()) and all(key in user.keys() for key in col)):
        return False
    return True

# Add a rule for the index page
@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/healthcheck')
def health_check():
    return jsonify({"alive": True})

@app.route('/users', methods=['POST', 'GET'])
def users():
    global n_user
    global db
    global col

    if request.method == 'POST':
        user = request.json
        if not user_validation(user):
            return "invalid JSON", 400

        user['id'] = n_user
        n_user += 1
        db.append(user)
        data = jsonify(user)
        return data, 200

    if request.method == 'GET':
        data = jsonify({"users": db})
        return data, 200

@app.route('/users/<id>', methods=['GET', 'PUT', 'DELETE'])
def user(id):
    user = False

    for i in range(len(db)):
        if db[i]['id'] == int(id): 
            user = db[i]
            index = i
            break

    if not user:
        return "id not found", 404

    if request.method == 'GET':
        data = jsonify(user)
        return data, 200
        
    if request.method == 'PUT':
        new_user = request.json
        if not user_validation(new_user):
            return "invalid JSON", 400

        new_user['id'] = user['id']
        db.pop(index)
        db.append(new_user)
        data = jsonify(new_user)
        print(new_user)
        return data, 200

    if request.method == 'DELETE':
        db.pop(index)
        data = jsonify({"success": True})
        return data, 200

@app.route('/login', methods=['POST'])
def login():
    content = request.json

    if 'username' in content.keys() and 'password' in content.keys():
        for i in range(len(db)):
            if db[i]['username'] == content['username'] and db[i]['password'] == content['password']:
                data = jsonify({"login": True})
                print(data)
                return data, 200
                
    data = jsonify({"login": False})
    return data, 200


# Run the application
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production application.
    app.debug = True
    app.run(host="0.0.0.0", debug=True)
