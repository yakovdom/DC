import json
from tornado import httpserver
from tornado import gen
from tornado.ioloop import IOLoop
import tornado.web
from db import DB
from auth import Authorizer
from config import get_config
config = get_config()
SERVICE_PORT = config['server']['port']

items = DB()
authorizer = Authorizer()


def check_authorization_and_fields(handler, necessary=[]):
    global authorizer
    body = json.loads(handler.request.body)
    for field in necessary:
        if field not in body:
            handler.set_status(400, 'Bad request')
            response = {'result': 'error', 'error_message': 'Bad request: need field \'{}\''.format(field)}
            handler.write(response)
            return False

    token = handler.request.headers.get('token')
    if token is None or not authorizer.validate(token):
        handler.set_status(401, 'Unauthorized')
        response = {'result': 'error', 'error_message': 'Unauthorized'}
        handler.write(response)
        return False
    return True


def process_db_answer(handler, response, code, headers):
    for k, v in headers.items():
        try:
            handler.set_header(k, v)
        except Exception as e:
            response['ooo'] = '{}'.format(e)
            response['k'] = k
            response['v'] = v
    if (code // 100 * 100) == 200:
        handler.set_status(code, 'OK')
        handler.write(response)
    else:
        handler.set_status(code, response['error_message'])
        handler.write(response)


class ItemHandler(tornado.web.RequestHandler):
    def post(self):
        global items
        if not check_authorization_and_fields(self, ['name', 'id', 'category']):
            return

        body = json.loads(self.request.body)
        name = body['name']
        id = body['id']
        category = body['category']
        process_db_answer(self, *items.add(id, name, category))

    def get(self):
        global items, authorizer
        if not check_authorization_and_fields(self, ['id']):
            return

        body = json.loads(self.request.body)
        id = body.pop('id')
        process_db_answer(self, *items.get_by_id(id))

    def put(self):
        global items
        if not check_authorization_and_fields(self, ['id']):
            return

        body = json.loads(self.request.body)
        id = body.pop('id')

        process_db_answer(self, *items.update(id, body['name'], body['category']))

    def delete(self):
        global items
        if not check_authorization_and_fields(self, ['id']):
            return

        body = json.loads(self.request.body)
        id = body.pop('id')

        process_db_answer(self, *items.delete(id))


class ItemsHandler(tornado.web.RequestHandler):
    def get(self):
        global items
        if not check_authorization_and_fields(self):
            return

        pagination_id = self.request.headers.get('pagination_id')

        process_db_answer(self, *items.get_all(pagination_id))


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/item", ItemHandler),
            (r"/items", ItemsHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


def main():
    app = Application()
    app.listen(SERVICE_PORT)
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
