import pymongo
from pymongo import MongoClient
import uuid
from config import get_config
config = get_config()
MONGO_HOST = config['mongo']['host']
MONGO_PORT = config['mongo']['port']
#OBJECS_PER_PAGE = config['server']['objects_per_page']
OBJECS_PER_PAGE = 1


class DB:
    def __init__(self):
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client.shop
        self.items = db.items
        self.pagination = db.pagination

    def add(self, id, name, category):
        try:
            if self.get_by_id(id)[1] == 200:
                response = {'result': 'Error', 'error_message': 'Item with id \'{}\' already exists'.format(id)}
                code = 401
            else:
                self.items.insert_one({'id': id, 'name': name, 'category': category})
                response = {'result': 'OK'}
                code = 200
        except:
            response = {'result': 'error', 'error_message': 'Server error'}
            code = 500

        return response, code, {}

    def get_all(self, pagination_id):

        try:
            stage = 0

            if pagination_id:
                pagination = self.pagination.find_one_and_delete({'id': pagination_id})
                stage = pagination['stage']

            items = self.items.find({}).sort("name", pymongo.ASCENDING).skip(stage * OBJECS_PER_PAGE).limit(OBJECS_PER_PAGE)
            result = list()
            for item in items:
                item.pop('_id')
                result.append(item)
            stage += 1
            pagination_id = str(uuid.uuid1())
            pagination = {
                "id": pagination_id,
                "stage": stage
            }
            self.pagination.insert_one(pagination)
            headers = {'pagination_id': pagination_id}
            response = {'result': 'OK', 'items': result}
            code = 200
        except Exception as e:
            response = {'result': 'Error', 'error_message': 'Server error {}'.format(e)}
            code = 500
            headers = {}

        return response, code, headers

    def get_by_id(self, id):
        try:
            item = self.items.find_one({'id': id})
            if item is None:
                response = {'result': 'Error', 'error_message': 'Item with id \'{}\' not found'.format(id)}
                code = 404
            else:
                item.pop('_id')
                response = {'result': 'OK', 'item': item}
                code = 200
        except:
            response = {'result': 'Error', 'error_message': 'Server error'}
            code = 500
        return response, code, {}

    def update(self, id, name, category):
        try:
            if self.get_by_id(id)[1] != 200:
                response = {'result': 'Error', 'error_message': 'Item with id \'{}\' not found'.format(id)}
                code = 404
            else:
                self.items.update_one({'id': id}, {'$set': {'name': name, 'category': category}})
                response = {'result': 'OK'}
                code = 200
        except:
            response = {'result': 'Error', 'error_message': 'Server error'}
            code = 500

        return response, code, {}

    def delete(self, id):
        try:
            if self.get_by_id(id)[1] != 200:
                response = {'result': 'Error', 'error_message': 'Item with id \'{}\' not found'.format(id)}
                code = 404
            else:
                self.items.delete_one({'id': id})
                response = {'result': 'OK'}
                code = 200
        except:
            response = {'result': 'Error', 'error_message': 'Server error'}
            code = 500

        return response, code, {}
