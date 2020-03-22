import json
from tornado import httpserver
from tornado import gen
from tornado.ioloop import IOLoop
import tornado.web
from db import DB
from auth import Authorizer

items = DB()
authorizer = Authorizer()


class ItemHandler(tornado.web.RequestHandler):
    def post(self):
        global items, authorizer

        body = json.loads(self.request.body)
        necessary = ['name', 'id', 'category', 'token']

        for field in necessary:
            if field not in body:
                self.set_status(400, 'Bad request')
                response = {'result': 'error', 'error_message': 'Bad request: need field \'{}\''.format(field)}
                self.write(response)
                return

        token = body.pop('token')
        if not authorizer.validate(token):
            self.set_status(401, 'Unauthorized ')
            response = {'result': 'error', 'error_message': 'Unauthorized'}
            self.write(response)
            return

        name = body['name']
        id = body['id']
        category = body['category']
        response = items.add(id, name, category)
        self.write(response)

    def get(self):
        global items, authorizer
        body = json.loads(self.request.body)
        necessary = ['id', 'token']

        for field in necessary:
            if field not in body:
                self.set_status(400, 'Bad request')
                response = {'result': 'error', 'error_message': 'Bad request: expected field \'{}\''.format(field)}
                self.write(response)
                return

        token = body.pop('token')
        if not authorizer.validate(token):
            self.set_status(401, 'Unauthorized ')
            response = {'result': 'error', 'error_message': 'Unauthorized'}
            self.write(response)
            return

        id = body.pop('id')
        response = items.get_by_id(id)
        self.write(response)

    def put(self):
        global items, authorizer
        body = json.loads(self.request.body)
        necessary = ['id', 'token']

        for field in necessary:
            if field not in body:
                self.set_status(400, 'Bad request')
                response = {'result': 'error', 'error_message': 'Bad request: expected field \'{}\''.format(field)}
                self.write(response)
                return

        token = body.pop('token')
        if not authorizer.validate(token):
            self.set_status(401, 'Unauthorized ')
            response = {'result': 'error', 'error_message': 'Unauthorized'}
            self.write(response)
            return

        id = body.pop('id')

        response = items.update(id, body['name'], body['category'])
        self.write(response)

    def delete(self):
        global items, authorizer
        body = json.loads(self.request.body)
        necessary = ['id', 'token']

        for field in necessary:
            if field not in body:
                self.set_status(400, 'Bad request')
                response = {'result': 'error', 'error_message': 'Bad request: expected field \'{}\''.format(field)}
                self.write(response)
                return

        token = body.pop('token')
        if not authorizer.validate(token):
            self.set_status(401, 'Unauthorized ')
            response = {'result': 'error', 'error_message': 'Unauthorized'}
            self.write(response)
            return

        id = body.pop('id')

        response = items.delete(id)
        self.write(response)


class ItemsHandler(tornado.web.RequestHandler):
    def get(self):
        global items, authorizer
        body = json.loads(self.request.body)
        necessary = ['id', 'token']
        for field in necessary:
            if field not in body:
                self.set_status(400, 'Bad request')
                response = {'result': 'error', 'error_message': 'Bad request: expected field \'{}\''.format(field)}
                self.write(response)
                return

        token = body.pop('token')
        if not authorizer.validate(token):
            self.set_status(401, 'Unauthorized ')
            response = {'result': 'error', 'error_message': 'Unauthorized'}
            self.write(response)
            return

        response = items.get_all()
        self.write(response)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/item", ItemHandler),
            (r"/items", ItemsHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


def main():
    app = Application()
    app.listen(3333)
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
