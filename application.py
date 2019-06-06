import os

import json

import copy

import datetime

import atexit

from flask import Flask, request, abort, make_response

from apscheduler.schedulers.background import BackgroundScheduler

import skypebot


from data import MESSAGE_WORKPIECE

from config import Config

from filters import tmsp_filter

from tools import DatabaseClient, create_answer


app = Flask(__name__)
app.config.from_object(Config)
app.config['DEBUG'] = True
app.template_folder = os.path.join(app.config['BASE_DIR'], 'templates')
tmsp_filter = app.template_filter()(tmsp_filter)

bot = skypebot.SkypeBot(app.config['APP_ID'], app.config['APP_PASS'])
db_instance = DatabaseClient(app.config['DB_URI'],
                             app.config['DB_NAME'],
                             app.config['COLLECTION_NAME'])

cron = BackgroundScheduler()
cron.add_job(func=db_instance.delete_all_docs, trigger='interval', seconds=3000)
cron.start()


@app.route('/')
def hello():
    return 'Hello! I\'m working just now!'


@app.route('/api/messages', methods=['GET', 'POST', ])
def webhook():
    if request.method == 'POST':
        try:
            data = json.loads(request.data)
            payload = copy.deepcopy(MESSAGE_WORKPIECE)

            now = datetime.datetime.utcnow()
            now_str = now.isoformat(timespec='milliseconds')

            payload['serviceUrl'] = data['serviceUrl']
            payload['type'] = data['type']
            payload['from']['id'] = data['recipient']['id']
            payload['from']['name'] = data['recipient']['name']
            payload['recipient']['id'] = data['from']['id']
            payload['recipient']['name'] = data["from"]['name']
            payload['conversation']['id'] = data['conversation']['id']
            payload['replyToId'] = data['id']
            payload['timestamp'] = now_str
            answer = create_answer(db_instance, data)
            payload['text'] = answer if answer else '(unamused)'

            bot.send_message(payload)
            
        except KeyError as error:
            abort(403)

    return make_response('Code 200')


atexit.register(lambda: cron.shutdown())
