from tools.message_handlers import create_answer, get_local_now
from tools.static_data import MESSAGE


def invitation_handler(request_data, db_instance):
    local_tz_name = request_data['entities'][0]['timezone']
    # entities = request_data.get('entities') or [{'timezone': 'Europe/Uzhgorod', }, ]
    # local_tz_name = entities[0]['timezone']
    db_instance.set_tz(local_tz_name)


def message_handler(request_data, db_instance):
    local_tz_name = request_data['entities'][0]['timezone']
    # entities = request_data.get('entities') or [{'timezone': 'Europe/Uzhgorod', }, ]
    # local_tz_name = entities[0]['timezone']
    local_dt = get_local_now(local_tz_name)
    local_dt_str = local_dt.isoformat()

    answer = create_answer(db_instance, request_data)

    MESSAGE['serviceUrl'] = request_data['serviceUrl']
    MESSAGE['type'] = request_data['type']
    MESSAGE['from']['id'] = request_data['recipient']['id']
    MESSAGE['from']['name'] = request_data['recipient']['name']
    MESSAGE['recipient']['id'] = request_data['from']['id']
    MESSAGE['recipient']['name'] = request_data["from"]['name']
    MESSAGE['conversation']['id'] = request_data['conversation']['id']
    MESSAGE['replyToId'] = request_data['id']
    MESSAGE['timestamp'] = local_dt_str
    MESSAGE['text'] = answer

    return MESSAGE
