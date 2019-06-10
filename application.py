import os

import atexit

import json

from pytz import reference

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from flask import Flask, request, make_response

from config import Config

import skypebot

from tools.template_filters import tmsp_filter

from tools.db_client import DatabaseClient

from tools.request_handlers import invitation_handler, message_handler


logging.basicConfig(filename='bbot.log',
                    level=logging.DEBUG,
                    format='%(levelname)s:%(message)s')

app = Flask(__name__)
app.config.from_object(Config)
app.config['DEBUG'] = True
app.template_folder = os.path.join(app.config['BASE_DIR'], 'templates')
tmsp_filter = app.template_filter()(tmsp_filter)

bot = skypebot.SkypeBot(app.config['APP_ID'],
                        app.config['APP_PASS'],
                        app.config['BOT_NAME'])

db_instance = DatabaseClient(app.config['DB_URI'],
                             app.config['DB_NAME'])

dt_localizer = reference.LocalTimezone()

cron = BackgroundScheduler()
cron.add_job(func=db_instance.delete_all_docs, trigger='interval', seconds=3000)
cron.start()


@app.route('/')
def hello():
    return 'Hello! I\'m working just now!'


@app.route('/api/messages', methods=['GET', 'POST', ])
def webhook():
    if request.method == 'POST':
        response_msg = None
        try:
            request_data = json.loads(request.data)
            if request_data.get('membersAdded') is not None:
                members_added = request_data['membersAdded']
                members_added = [member['name'] for member in members_added]
                if bot.name in members_added:
                    invitation_handler(request_data, db_instance, dt_localizer)
                    response_msg = 'invitation accepted!'

            if request_data['type'] == 'message':
                payload = message_handler(request_data, db_instance)
                bot.send_message(payload)
                response_msg = 'message sent'

            return make_response(response_msg, 200)
        except KeyError as error:
            logging.error(error)
            return make_response('Bad request', 400)

    return make_response('Got it', 200)


atexit.register(lambda: cron.shutdown())
