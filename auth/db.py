from pymongo import MongoClient
import uuid
import time
import json
from messageQueue import MessageQueue
from config import get_config
config = get_config()
MONGO_HOST = config['mongo']['host']
MONGO_PORT = config['mongo']['port']

ACCESS_TTL = config['auth']['access_ttl']
REFRESH_TTL = config['auth']['refresh_ttl']

def get_time():
    return time.time() / 1000


import hashlib, binascii, os

def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

class DB:
    def __init__(self):
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client.auth
        self.users = db.users
        try:
            self.queue = MessageQueue()
        except Exception as ex:
            from sys import stdout as st
            st.write('\n\nEx: {}\n\n'.format(ex))
            st.flush()
            raise ex

    def _find(self, login):
        return self.users.find_one({'login': login})

    def _has(self, login):
        return self._find(login) is not None

    def _generate_tokens(self):
        access_token = str(uuid.uuid1())
        refresh_token = str(uuid.uuid1())
        return access_token, refresh_token

    def sign_up(self, login, password):
        if self._has(login):
            return 200, 'ok', {'result': 'This login is already in use'}

        id = str(uuid.uuid1())
        link = "{}:{}/confirm/{}".format('localhost', config['auth']['port'], id)
        self.users.insert_one({'login': login, 'password': hash_password(password), 'confirmation_id': id, 'role': 'user'})
        self.queue.send_message(json.dumps({"link": link, "login": login}))
        return 200, 'ok', {'result': 'ok', 'link': link}

    def confirm(self, confirmation_id):
        user = self.users.find_one({'confirmation_id': confirmation_id})
        if user is None:
            return 404, 'Not found', {'result': 'Unknown confirmation link'}

        self.users.update_one({'login': user['login']},
                              {'$set': {'confirmation_id': None}})


        return 200, 'ok', {'result': 'ok'}

    def sign_in(self, login, password):
        user = self._find(login)
        if user is None or not verify_password(user['password'], password):
            return 403, 'Forbidden', {'result': 'error', 'error_message': 'Wrong login or password'}

        if user.get('confirmation_id'):
            return 403, 'Forbidden', {'result': 'error', 'error_message': 'Confirm email'}

        access_token, refresh_token = self._generate_tokens()

        self.users.update_one({'login': login},
                              {'$set': {'access_token': access_token,
                                        'refresh_token': refresh_token,
                                        'ts': get_time()}})

        return 200, 'ok', {'result': 'ok', 'access_token': access_token, 'refresh_token': refresh_token}

    def validate(self, token):
        user = self.users.find_one({'access_token': token})
        ts = get_time()
        if user is None or (ts - user.get('ts', 0) > ACCESS_TTL):
            return 404, 'Not found', {'result': 'Unknown access token'}
        return 200, 'ok', {'result': 'ok', 'role': user.get('role')}

    def refresh(self, token):
        user = self.users.find_one({'refresh_token': token})
        ts = get_time()
        if user is None or (ts - user.get('ts', 0) > REFRESH_TTL):
            return 404, 'Not found', {'result': 'Unknown refresh token'}

        access_token, refresh_token = self._generate_tokens()
        self.users.update_one({'refresh_token': token},
                              {'$set': {'access_token': access_token,
                                        'refresh_token': refresh_token,
                                        'ts': time.monotonic()}})

        return 200, 'ok', {'result': 'ok', 'access_token': access_token, 'refresh_token': refresh_token}

    def set_as_admin(self, login):
        user = self.users.find_one({'login': login})
        if user is None:
            return 404, 'Not found', {'result': 'Unknown login'}

        self.users.update_one({'login': login},
                              {'$set': {'role': 'admin'}})

        return 200, 'ok', {'result': 'ok'}
