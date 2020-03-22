from pymongo import MongoClient

MONGO_HOST = "mongo"
MONGO_PORT = 27017


class DB:
    def __init__(self):
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client.shop
        self.items = db.items

    def add(self, id, name, category):
        try:
            if self.get_by_id(id)['result'] == 'OK':
                response = {'result': 'Error', 'error_message': 'Item with id \'{}\' already exists'.format(id)}
            else:
                self.items.insert_one({'id': id, 'name': name, 'category': category})
                response = {'result': 'OK'}
        except:
            response = {'result': 'error', 'error_message': 'Server error'}

        return response

    def get_all(self):
        try:
            items = self.items.find({})
            print(items)
            result = list()
            for item in items:
                item.pop('_id')
                result.append(item)
            response = {'result': 'OK', 'items': result}
        except:
            response = {'result': 'Error', 'error_message': 'Server error'}

        return response

    def get_by_id(self, id):
        try:
            item = self.items.find_one({'id': id})
            if item is None:
                response = {'result': 'Error', 'error_message': 'Item with id \'{}\' not found'.format(id)}
            else:
                item.pop('_id')
                response = {'result': 'OK', 'item': item}
        except:
            response = {'result': 'Error', 'error_message': 'Server error'}
        return response

    def update(self, id, name, category):
        try:
            if self.get_by_id(id)['result'] != 'OK':
                response = {'result': 'Error', 'error_message': 'Item with id \'{}\' not found'.format(id)}
            else:
                self.items.update_one({'id': id}, {'$set': {'name': name, 'category': category}})
                response = {'result': 'OK'}
        except:
            response = {'result': 'Error', 'error_message': 'Server error'}

        return response

    def delete(self, id):
        try:
            if self.get_by_id(id)['result'] != 'OK':
                response = {'result': 'Error', 'error_message': 'Item with id \'{}\' not found'.format(id)}
            else:
                self.items.delete_one({'id': id})
                response = {'result': 'OK'}
        except:
            response = {'result': 'Error', 'error_message': 'Server error'}

        return response
