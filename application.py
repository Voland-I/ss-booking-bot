import os

import atexit

import json

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from flask import Flask, request, make_response, views

from config import Config

import skypebot

from tools.db_client import DatabaseClient

from tools.request_handlers import invitation_handler, message_handler


logging.basicConfig(filename='bbot.log',
                    level=logging.DEBUG,
                    format='%(levelname)s:%(message)s')

app = Flask(__name__)
app.config.from_object(Config)
app.template_folder = os.path.join(app.config['BASE_DIR'], 'templates')

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
            if request_data.get('membersAdded') is not None:
                members_added = request_data['membersAdded']
                members_added = [member['name'] for member in members_added]
                if bot.name in members_added:
                    invitation_handler(request_data, db_instance)
                    response_msg = 'invitation accepted!'

            if request_data['type'] == 'message':
                payload = message_handler(request_data, db_instance)
                bot.send_message(payload)
                response_msg = 'message sent'

            return make_response(response_msg, 200)
        except KeyError as error:
            logging.error(error)
            return make_response('Bad request', 400)


app.add_url_rule('/api/messages', view_func=WebHook.as_view('webhook'))

atexit.register(lambda: db_cron.shutdown())
