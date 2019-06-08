from datetime import datetime

from tools.messege_handlers import create_answer, get_now_local_datetime
from tools.static_data import MESSAGE


def invitation_handler(request_data, db_instance, localtime):
    local_dt, _ = get_now_local_datetime(request_data)
    tz_name = localtime.tzname(local_dt)
    db_instance.set_tz(tz_name)


def message_handler(request_data, db_instance):
    _, now_local_str = get_now_local_datetime(request_data)

    answer = create_answer(db_instance, request_data)

    MESSAGE['serviceUrl'] = request_data['serviceUrl']
    MESSAGE['type'] = request_data['type']
    MESSAGE['from']['id'] = request_data['recipient']['id']
    MESSAGE['from']['name'] = request_data['recipient']['name']
    MESSAGE['recipient']['id'] = request_data['from']['id']
    MESSAGE['recipient']['name'] = request_data["from"]['name']
    MESSAGE['conversation']['id'] = request_data['conversation']['id']
    MESSAGE['replyToId'] = request_data['id']
    MESSAGE['timestamp'] = now_local_str
    MESSAGE['text'] = answer

    return MESSAGE
