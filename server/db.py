import sqlite3


class DB:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        self.conn = sqlite3.connect('my.sqlite')

        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
        self.conn.row_factory = dict_factory
        self.cursor = self.conn.cursor()

    def create(self):
        self.cursor.execute('''CREATE TABLE items (id varchar primary key, name varchar, category varchar)''')

    def add(self, id, name, category):
        try:
            self.cursor.execute("INSERT INTO items (id, name, category) VALUES ('{}','{}', '{}')".format(id, name, category))
            response = {'result': 'ok'}
        except sqlite3.DatabaseError as err:
            response = {'result': 'error', 'error_message': err}
        else:
            self.conn.commit()
        return response

    def close(self):
        self.cursor.close()
        self.conn.close()

    def get_all(self):
        try:
            all = []
            for row in self.cursor.execute('SELECT * FROM items'):
                all.append(row)
            response = {'result': 'OK', 'items': all}
        except sqlite3.DatabaseError as err:
            response = {'result': 'Error', 'error_message': 'Error'}
        else:
            self.conn.commit()
        return response

    def get_by_id(self, id):
        try:
            self.cursor.execute("SELECT * FROM items WHERE id == '{}'".format(id))
            row = self.cursor.fetchone()
            response = {'result': 'OK', 'item': row}
        except sqlite3.DatabaseError as err:
            response = {'result': 'Error', 'error_message': 'Item not found'}
        else:
            self.conn.commit()
        return response

    def update(self, id, name, category):
        try:
            self.cursor.execute("UPDATE items SET name = '{}', category = '{}' WHERE id == '{}'".format(name, category, id))
            response = {'result': 'OK'}
        except sqlite3.DatabaseError as err:
            response = {'result': 'Error', 'error_message': 'Item not found'}
        else:
            self.conn.commit()
        return response

    def delete(self, id):
        try:
            self.cursor.execute("DELETE FROM items WHERE id == '{}'".format(id))
            response = {'result': 'OK'}
        except sqlite3.DatabaseError as err:
            response = {'result': 'Error', 'error_message': 'Item not found '}
        else:
            self.conn.commit()
        return response
