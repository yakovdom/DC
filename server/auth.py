import grpc

import validation_pb2
import validation_pb2_grpc

from config import get_config
config = get_config()
AUTH_HOST = config['auth']['host']
AUTH_PORT = config['auth']['validation_port']

class Authorizer:
    def validate(self, token, action):
        channel = grpc.insecure_channel('{}:{}'.format(AUTH_HOST, AUTH_PORT))
        stub = validation_pb2_grpc.ValidatorStub(channel)
        request = validation_pb2.ValidationRequest(token=token, action=action)
        response = stub.Validate(request)
        print(response.is_valid)
        return response.is_valid

