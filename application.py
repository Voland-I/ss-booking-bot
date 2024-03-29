import os
import logging
import json
import atexit

from flask import Flask, request, make_response, views
from apscheduler.schedulers.background import BackgroundScheduler

import config
import skypebot
from tools.db_client import DatabaseClient
from tools.message_processing import message_handler


logging.basicConfig(filename='bbot.log',
                    level=logging.DEBUG,
                    format='%(levelname)s:%(message)s')

app = Flask(__name__)
app.config.from_object(config.Config)
app.template_folder = os.path.join(app.config['BASE_DIR'],
                                   'templates')

bot = skypebot.SkypeBot()

db_instance = DatabaseClient(app.config['DB_URI'],
                             app.config['DB_NAME'])

db_cron = BackgroundScheduler()
db_cron.add_job(func=db_instance.delete_all_docs,
                trigger='interval',
                seconds=3000)

db_cron.start()


class Hello(views.MethodView):
    def get(self):
        return f'Hello, my name is {app.config["BOT_NAME"]}'


class WebHook(views.MethodView):
    def get(self):
        return make_response(app.config['BOT_NAME'], 200)

    def post(self):
        try:
            response_msg = ''
            request_data = json.loads(request.data)
            if request_data['type'] == 'message':
                payload = message_handler(request_data,
                                          db_instance)
                bot.send_message(payload)
                response_msg = 'message sent'

        except KeyError as error:
            logging.error(error)
            return make_response('Bad request', 400)
        else:
            return make_response(response_msg, 200)


app.add_url_rule('/api/messages',
                 view_func=WebHook.as_view('webhook'))

atexit.register(lambda: db_cron.shutdown())
