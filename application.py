import logging
import json
import atexit

from flask import Flask, request, make_response, views
from apscheduler.schedulers.background import BackgroundScheduler

import config
import skypebot
from tools.db_client import DatabaseClient
from tools.message_processing import get_response_message


logging.basicConfig(filename='bbot.log',
                    level=logging.DEBUG,
                    format='%(levelname)s:%(message)s')

app = Flask(__name__)
app.config.from_object(config.Config)

bot = skypebot.SkypeBot()

db_instance = DatabaseClient(app.config['DB_URI'],
                             app.config['DB_NAME'])

db_cron = BackgroundScheduler()
db_cron.add_job(func=db_instance.delete_all_docs,
                trigger='interval',
                seconds=3000)

app_cron = BackgroundScheduler()
app_cron.add_job(func=bot.fake_request,
                 trigger='interval',
                 seconds=30)

db_cron.start()
app_cron.start()


class Hello(views.MethodView):
    def get(self):
        bot_name = app.config["BOT_NAME"]
        return f'Hello, my name is {bot_name}'


class WebHook(views.MethodView):
    def get(self):
        bot_name = app.config['BOT_NAME']
        return make_response(bot_name, 200)

    def post(self):
        try:
            request_data = json.loads(request.data)
            if request_data['type'] == 'message':
                payload = get_response_message(request_data, db_instance)
                bot.send_message(payload)

        except KeyError as error:
            logging.error(error)
            return make_response('Bad request', 400)


app.add_url_rule('/api/messages', view_func=WebHook.as_view('webhook'))
app.add_url_rule('/', view_func=Hello.as_view('hello'))

atexit.register(lambda: db_cron.shutdown())
atexit.register(lambda: app_cron.shutdown())
