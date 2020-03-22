from pymongo import MongoClient
import uuid
import time

MONGO_HOST = "mongo"
MONGO_PORT = 27017

ACCESS_TTL = 3000
REFRESH_TTL = 6000

class DB:
    def __init__(self):
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client.auth
        self.users = db.users

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

        self.users.insert_one({'login': login, 'password': password})
        # return 504, 'Gateway timeout', {'result': 'error', 'error_message': 'Gateway timeout'}

        return 200, 'ok', {'result': 'ok'}

    def sign_in(self, login, password):
        user = self._find(login)
        if user is None or user['password'] != password:
            return 200, 'ok', {'result': 'error', 'error_message': 'Wrong login or password'}

        access_token, refresh_token = self._generate_tokens()

        self.users.update_one({'login': login},
                              {'$set': {'access_token': access_token,
                                        'refresh_token': refresh_token,
                                        'ts': time.monotonic()}})

        # return 504, 'Gateway timeout', {'result': 'error', 'error_message': 'Gateway timeout'}
        return 200, 'ok', {'result': 'ok', 'access_token': access_token, 'refresh_token': refresh_token}

    def validate(self, token):
        user = self.users.find_one({'access_token': token})
        ts = time.monotonic()
        if user is None or (ts - user.get('ts', 0) > ACCESS_TTL):
            return 200, 'ok', {'result': 'Unknown access token'}
        # return 504, 'Gateway timeout', {'result': 'error', 'error_message': 'Gateway timeout'}
        return 200, 'ok', {'result': 'ok'}

    def refresh(self, token):
        user = self.users.find_one({'refresh_token': token})
        ts = time.monotonic()
        if user is None or (ts - user.get('ts', 0) > REFRESH_TTL):
            return 200, 'ok', {'result': 'Unknown refresh token'}

        access_token, refresh_token = self._generate_tokens()
        self.users.update_one({'refresh_token': token},
                              {'$set': {'access_token': access_token,
                                        'refresh_token': refresh_token,
                                        'ts': time.monotonic()}})

        # return 504, 'Gateway timeout', {'result': 'error', 'error_message': 'Gateway timeout'}
        return 200, 'ok', {'result': 'ok', 'access_token': access_token, 'refresh_token': refresh_token}
