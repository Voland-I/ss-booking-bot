from datetime import datetime

import copy

from static_data import MESSAGE_WORKPIECE

from tools import create_answer


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
    payload = copy.deepcopy(MESSAGE_WORKPIECE)

    payload['serviceUrl'] = request_data['serviceUrl']
    payload['type'] = request_data['type']
    payload['from']['id'] = request_data['recipient']['id']
    payload['from']['name'] = request_data['recipient']['name']
    payload['recipient']['id'] = request_data['from']['id']
    payload['recipient']['name'] = request_data["from"]['name']
    payload['conversation']['id'] = request_data['conversation']['id']
    payload['replyToId'] = request_data['id']
    payload['timestamp'] = now_local_str
    answer = create_answer(db_instance, request_data)
    payload['text'] = answer

    return payload


















