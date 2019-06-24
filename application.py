import logging
import json
import atexit

from flask import Flask, request, make_response, views
from apscheduler.schedulers.background import BackgroundScheduler

import config
import skypebot
from tools.db_client import DatabaseClient
from tools.message_processing import message_processing
from tools.time_tools import get_tzname_from_request
from tools.system_tools import get_value_from_env
from tools.users_manage import conversation_update_processing
from tools.commands_processing import CommandsProcessor


logging.basicConfig(filename='bbot.log',
                    level=logging.DEBUG,
                    format='%(levelname)s:%(message)s')

app = Flask(__name__)
app.config.from_object(config.Config)

bot = skypebot.SkypeBot()

db_instance = DatabaseClient(app.config['DB_URI'],
                             app.config['DB_NAME'])

command_processor = CommandsProcessor(db_instance)

db_cron = BackgroundScheduler()
db_cron.add_job(func=db_instance.delete_all_docs,
                trigger='interval',
                seconds=30)

app_cron = BackgroundScheduler()
app_cron.add_job(func=bot.fake_request,
                 trigger='interval',
                 seconds=30)

db_cron.start()
app_cron.start()


class WebHook(views.MethodView):
    def get(self):
        bot_name = get_value_from_env('BOT_NAME')
        return make_response(bot_name, 200)

    def post(self):
        try:
            request_data = json.loads(request.data)
            request_type = request_data['type']
            group_id = request_data['conversation']['id']
            tzname = get_tzname_from_request(request_data)
            db_instance.set_collection_and_tzname_if_not_exist(group_id, tzname)
            if request_type == 'message':
                payload = message_processing(db_instance, command_processor, request_data)
                bot.send_message(payload)
            if request_type == 'conversationUpdate':
                payload = conversation_update_processing(db_instance, request_data)
                bot.send_message(payload)

        except KeyError as error:
            logging.error(error)
            return make_response('Bad request', 400)

        return make_response('Got it!', 200)


app.add_url_rule('/api/messages', view_func=WebHook.as_view('webhook'))

atexit.register(lambda: db_cron.shutdown())
atexit.register(lambda: app_cron.shutdown())
