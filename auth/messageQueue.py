import pika
from config import get_config
config = get_config()
QUEUE_HOST = config['rabbitmq']['host']
QUEUE_PORT = config['rabbitmq']['port']
QUEUE_LOGIN = config['rabbitmq']['user']
QUEUE_PSWD = config['rabbitmq']['password']
QUEUE_NAME = config['rabbitmq']['queue']

class MessageQueue:
    def __init__(self):
        credentials = pika.PlainCredentials(QUEUE_LOGIN, QUEUE_PSWD)
        self.parameters = pika.ConnectionParameters(QUEUE_HOST,
                                               QUEUE_PORT,
                                               '/',
                                               credentials)


    def _connect(self):
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=QUEUE_NAME)

    def send_message(self, message):
        try:
            self.channel.basic_publish(exchange='',
                                  routing_key=QUEUE_NAME,
                                  body=message)
        except Exception as ex:
            from sys import stdout as st
            st.write('\n\ntrouble {} \n\n'.format(ex))
            st.flush()
            self._connect()
            self.send_message(message)


    def close(self):
        self.connection.close()