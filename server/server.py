import json
from tornado import httpserver
from tornado import gen
from tornado.ioloop import IOLoop
import tornado.web
from db import DB

items = DB()
try:
    items.create()
except:
    pass

class CreateHandler(tornado.web.RequestHandler):
    def post(self):
        global items
        print('__ADD__')
        try:
            body = json.loads(self.request.body)
            name = body['name']
            id = body['id']
            category = body['category']
            '''
            if id in items.storage:
                raise Exception('item {} already exists'.format(id))
            items.storage[id] = Item(name, id, category)
            response = {'result': 'ok'}
            '''
            response = items.add(id, name, category)
            print(response)
            self.write(response)
        except Exception as e:
            response = {'result': 'error', 'error_message': 'Can\'t add item: {}'.format(e)}
            self.write(response)


class ShowAllHandler(tornado.web.RequestHandler):
    def get(self):
        global items
        print('__SHOW_ALL__')
        # response = items.to_json()
        # response['result'] = 'ok'
        response = items.get_all()
        print(response)
        self.write(response)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        global items
        print(self.request.headers)
        id = self.request.uri[1:]
        response = items.get_by_id(id)
        self.write(response)

    def put(self):
        global items
        id = self.request.uri[1:]
        print('__UPDATE__')
        body = json.loads(self.request.body)
        if 'name' not in body:
            self.write({'result': 'error', 'error_message': 'boby has no \'name\''})
            return
        if 'category' not in body:
            self.write({'result': 'error', 'error_message': 'boby has no \'category\''})
            return
        response = items.update(id, body['name'], body['category'])
        self.write(response)

    def delete(self):
        global items
        id = self.request.uri[1:]
        response = items.delete(id)
        self.write(response)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/create", CreateHandler),
            (r"/showall", ShowAllHandler),
            (r"/.*", MainHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


def main():
    app = Application()
    app.listen(3333)
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
