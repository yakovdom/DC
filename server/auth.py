import requests
import json

AUTH_HOST = 'auth'
AUTH_PORT = '2222'


class Authorizer:
    def validate(self, token):
        url = 'http://{}:{}/validate'.format(AUTH_HOST, AUTH_PORT)
        body = json.dumps({'access_token': token})
        response = json.loads(requests.post(url, data=body).text)
        return response['result'] == 'ok'
