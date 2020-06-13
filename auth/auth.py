import json
from tornado.ioloop import IOLoop
import time
import tornado.gen
import tornado.web
from db import DB
from config import get_config
import grpc
from concurrent import futures
import validation_pb2
import validation_pb2_grpc
import threading
config = get_config()
SERVICE_PORT = config['auth']['port']
VALIDATION_PORT = config['auth']['validation_port']

db = DB()

class SignUpHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            body = json.loads(self.request.body)
            login = body['login']
            password = body['password']
            status, message, response = db.sign_up(login, password)
            self.set_status(status, message)
            self.write(response)
        except Exception as e:
            self.set_status(400, 'Bad request')
            response = {'result': 'error', 'error_message': 'Bad request'}
            self.write(response)


class SignInHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            body = json.loads(self.request.body)
            login = body['login']
            password = body['password']
            status, message, response = db.sign_in(login, password)
            self.set_status(status, message)
            if status == 200:
                self.set_header('access_token', response.pop('access_token'))
                self.set_header('refresh_token', response.pop('refresh_token'))
            self.write(response)
        except Exception as e:
            self.set_status(400, 'Bad request')
            response = {'result': 'error', 'error_message': 'Bad request {}'.format(e)}

            self.write(response)


class RefreshHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            refresh_token = self.request.headers.get('token')
            status, message, response = db.refresh(refresh_token)
            self.set_status(status, message)
            if status == 200:
                self.set_header('access_token', response.pop('access_token'))
                self.set_header('refresh_token', response.pop('refresh_token'))
            self.write(response)
        except Exception as e:
            self.set_status(400, 'Bad request')
            response = {'result': 'error', 'error_message': 'Bad request {}'.format(e)}
            self.write(response)

'''
class ValidateHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            access_token = self.request.headers.get('token')
            status, message, response = db.validate(access_token)
            self.set_status(status, message)
            self.write(response)
        except Exception as e:
            self.set_status(400, 'Bad request')
            response = {'result': 'error', 'error_message': 'Bad request {}'.format(e)}
            self.write(response)
'''

class ChangeRoleHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            access_token = self.request.headers.get('token')
            status, message, response = db.validate(access_token)
            if status != 200:
                self.set_status(status, message)
                self.write(response)
                return

            if response.get('role') != 'admin':
                self.set_status(403, 'Forbidden')
                return

            body = json.loads(self.request.body)
            login = body['login']

            status, message, response = db.set_as_admin(login)
            self.set_status(status, message)
            self.write(response)
        except Exception as e:
            self.set_status(400, 'Bad request')
            response = {'result': 'error', 'error_message': 'Bad request {}'.format(e)}
            self.write(response)

class ConfirmHandler(tornado.web.RequestHandler):
    def get(self):
        id = self.request.path[len('/confirm/'):]
        from sys import stdout as st
        st.write('\nOK {} OK {} \n'.format(id, self.request.path))
        st.flush()
        try:
            status, message, response = db.confirm(id)
            self.set_status(status, message)
            self.write(response)
        except Exception as e:
            self.set_status(400, 'Bad request')
            response = {'result': 'error', 'error_message': 'Bad request {}'.format(e)}
            self.write(response)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/sign_up", SignUpHandler),
            (r"/sign_in", SignInHandler),
            (r"/refresh", RefreshHandler),
            (r"/change_role", ChangeRoleHandler),
            #(r"/validate", ValidateHandler),
            (r"/confirm/.*", ConfirmHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


def is_ok(role, action):
    from sys import stdout as st
    st.write('\n\nRole: {}, Action: {}\n\n'.format(role, action))
    st.flush()
    if role == 'admin':
        return True

    if role == 'user' and action == 'get_item':
        return True

    if role == 'user' and action == 'get_items':
        return True

    return False


def validate_impl(token):
    status, _, response = db.validate(token)
    return status, response.get('role')


class Validator(validation_pb2_grpc.ValidatorServicer):
    def Validate(self, request, context):
        access_token = request.token
        action = request.action
        response = validation_pb2.ValidationResponse()
        status, role = validate_impl(access_token)
        if status != 200:
            response.is_valid = False
        else:
            response.is_valid = is_ok(role, action)
        return response



def start_grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    validation_pb2_grpc.add_ValidatorServicer_to_server(Validator(), server)
    server.add_insecure_port('[::]:{}'.format(VALIDATION_PORT))
    server.start()
    server.wait_for_termination()

def main():
    t = threading.Thread(target=start_grpc_server, args=[])
    t.start()
    app = Application()
    app.listen(SERVICE_PORT)
    IOLoop.instance().start()



if __name__ == '__main__':
    main()
