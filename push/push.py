import json
from tornado import httpserver
from tornado import gen
from tornado.ioloop import IOLoop
import tornado.web
import smtplib
import pika
import time
from config import get_config
config = get_config()
LOGIN = config['push']['login']
PSWD = config['push']['password']
HOST = config['push']['provider_host']
PORT = config['push']['provider_port']
QUEUE_HOST = config['rabbitmq']['host']
QUEUE_PORT = config['rabbitmq']['port']
QUEUE_LOGIN = config['rabbitmq']['user']
QUEUE_PSWD = config['rabbitmq']['password']
QUEUE_NAME = config['rabbitmq']['queue']
SERVICE_PORT = config['push']['port']


class EmailManager:
    def __init__(self):
        self.smtpObj = smtplib.SMTP(HOST, PORT)
        self.smtpObj.starttls()
        self.smtpObj.login(LOGIN, PSWD)

    def send_email(self, to, text):
        self.smtpObj.sendmail(LOGIN, to, text)

    def close(self):
        self.smtpObj.quit()


emailManager = EmailManager()
channel = None


def callback(ch, method, properties, body):
    doc = json.loads(body)
    from sys import stdout as st
    st.write('\n\nGOT: {}\n\n'.format(doc))
    st.flush()
    message = 'Subject: {}\n\n{}'.format("Confirm your email", doc['link'])
    try:
        emailManager.send_email(doc['login'], message)
    except:
        channel.basic_publish(exchange='',
                                   routing_key=QUEUE_NAME,
                                   body=message)

def start_queue():
    while 42:
        try:
            credentials = pika.PlainCredentials(QUEUE_LOGIN, QUEUE_PSWD)
            parameters = pika.ConnectionParameters(QUEUE_HOST,
                                                  QUEUE_PORT,
                                                   '/',
                                                   credentials)
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME)
            channel.basic_consume(
                queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
            channel.start_consuming()
            return connection
        except:
            from sys import stdout as st
            st.write('\n\nWAIT\n\n')
            st.flush()
            time.sleep(10)



class MainHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            body = json.loads(self.request.body)
            necessary = ['text', 'email']
            for field in necessary:
                if field not in body:
                    self.set_status(401, 'Bad request')
                    self.write({'result': 'Error', 'error_message': 'Expected field "{}"'.format(field)})
                    return

            text = body['text']
            email = body['email']
            emailManager.send_email(email, text)
            self.set_status(200, 'OK')
        except Exception as ex:
            self.set_status(500, 'Server error')
            self.write({'result': 'Error', 'error_message': '{}'.format(ex)})
            print(ex.with_traceback())


class Application(tornado.web.Application):
    def __init__(self):
        connection = start_queue()
        handlers = [
            (r"/*", MainHandler),
        ]
        tornado.web.Application.__init__(self, handlers)


def main():
    app = Application()
    app.listen(SERVICE_PORT)
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
