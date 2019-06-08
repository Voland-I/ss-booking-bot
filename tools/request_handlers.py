from datetime import datetime

from tools.messege_handlers import create_answer
from tools.static_data import MESSAGE


def invitation_handler(request_data, db_instance, localtime):
    local_dt_str = request_data['localTimestamp']
    local_dt = datetime.fromisoformat(local_dt_str)
    tz_name = localtime.tzname(local_dt)
    db_instance.set_tz(tz_name)


def message_handler(request_data, db_instance):
    request_local_dt_str = request_data['localTimestamp']
    request_local_dt = datetime.fromisoformat(request_local_dt_str)
    now_utc = datetime.now()
    now_local = now_utc.replace(tzinfo=request_local_dt.tzinfo)
    now_local_str = now_local.isoformat()

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
