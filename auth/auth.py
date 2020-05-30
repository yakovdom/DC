import json
from tornado import httpserver
from tornado import gen
from tornado.ioloop import IOLoop
import tornado.web
from db import DB
from config import get_config
config = get_config()
SERVICE_PORT = config['auth']['port']

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
            (r"/validate", ValidateHandler),
            (r"/confirm/.*", ConfirmHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


def main():
    app = Application()
    app.listen(SERVICE_PORT)
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
