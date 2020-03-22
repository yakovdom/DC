import json
from tornado import httpserver
from tornado import gen
from tornado.ioloop import IOLoop
import tornado.web
from db import DB

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
            self.write(response)
        except Exception as e:
            self.set_status(400, 'Bad request')
            response = {'result': 'error', 'error_message': 'Bad request'}
            self.write(response)


class RefreshHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            body = json.loads(self.request.body)
            refresh_token = body['refresh_token']
            status, message, response = db.refresh(refresh_token)
            self.set_status(status, message)
            self.write(response)
        except Exception as e:
            self.set_status(400, 'Bad request')
            response = {'result': 'error', 'error_message': 'Bad request {}'.format(e)}
            self.write(response)


class ValidateHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            body = json.loads(self.request.body)
            access_token = body['access_token']
            status, message, response = db.validate(access_token)
            self.set_status(status, message)
            self.write(response)
        except Exception as e:
            self.set_status(400, 'Bad request')
            response = {'result': 'error', 'error_message': 'Bad request'}
            self.write(response)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/sign_up", SignUpHandler),
            (r"/sign_in", SignInHandler),
            (r"/refresh", RefreshHandler),
            (r"/validate", ValidateHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


def main():
    app = Application()
    app.listen(2222)
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
