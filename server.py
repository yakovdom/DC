import json
from tornado import httpserver
from tornado import gen
from tornado.ioloop import IOLoop
import tornado.web


class Item:
    def __init__(self, name, id, category):
        self.name = name
        self.id = id
        self.category = category

    def as_str(self):
        return 'name: {}, id: {}, category: {}\n'.format(self.name, self.id, self.category)

    def as_json(self):
        res = {
            'name': self.name,
            'id': self.id,
            'category': self.category
        }
        return res


class ItemStorage:
    def __init__(self):
        self.storage = dict()

    def to_str(self):
        result = ''
        for item in self.storage.values():
            result += item.as_str()
        return result

    def to_json(self):
        all = []
        for item in self.storage.values():
            all.append(item.as_json())
        return {'items': all}


items = ItemStorage()


class CreateHandler(tornado.web.RequestHandler):
    def post(self):
        global items
        print('__ADD__')
        try:
            body = json.loads(self.request.body)
            name = body['name']
            id = body['id']
            category = body['category']
            if id in items.storage:
                raise Exception('item {} already exists'.format(id))
            items.storage[id] = Item(name, id, category)
            response = {'result': 'ok'}
            self.write(response)
        except Exception as e:
            response = {'result': 'error', 'error_message': 'Can\'t add item: {}'.format(e)}
            self.write(response)


class ShowAllHandler(tornado.web.RequestHandler):
    def get(self):
        global items
        print('__SHOW_ALL__')
        response = items.to_json()
        response['result'] = 'ok'
        self.write(response)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        global items
        print(self.request.headers)
        id = self.request.uri[1:]
        if id in items.storage:
            print('__SHOW__')
            response = items.storage[id].as_json()
            response['result'] = 'ok'
            self.write(response)
        else:
            response = {'result': 'error', 'error_message': 'item {} not found'.format(id)}
            self.write(response)

    def put(self):
        global items
        id = self.request.uri[1:]
        print('__UPDATE__')
        if id in items.storage:
            body = json.loads(self.request.body)
            items.storage[id].name = body['name']
            items.storage[id].category = body['category']
            response = {'result': 'ok'}
            self.write(response)
        else:
            response = {'result': 'error', 'error_message': 'item {} not found'.format(id)}
            self.write(response)

    def delete(self):
        global items
        id = self.request.uri[1:]
        print('__DELETE__')
        if id in items.storage:
            items.storage.pop(id)
            response = {'result': 'ok'}
            self.write(response)
        else:
            response = {'result': 'error', 'error_message': 'item {} not found'.format(id)}
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

