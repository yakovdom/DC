import requests
import json
from config import get_config
config = get_config()
AUTH_HOST = config['auth']['host']
AUTH_PORT = config['auth']['port']

class Authorizer:
    def validate(self, token):
        url = 'http://{}:{}/validate'.format(AUTH_HOST, AUTH_PORT)
        #body = json.dumps({'access_token': token})
        # response = json.loads(requests.post(url, data=body).text)
        response = requests.get(
            url,
            headers={'token': token}
        )
        #response = json.loads(requests.get(url, data=body).text)
        return response.status_code == 200
