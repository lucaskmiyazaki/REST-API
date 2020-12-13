import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend

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
