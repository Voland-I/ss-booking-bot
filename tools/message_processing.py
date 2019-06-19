from datetime import datetime
import pytz

import re

from tools.static_data import ITEM_IN_DB, MESSAGE


def get_local_now(tzname):
    utc_now = datetime.utcnow().astimezone(pytz.UTC)
    local_tz = pytz.timezone(tzname)
    local_now = utc_now.astimezone(local_tz)
    return local_now


def make_row_from_item(item):
    start_time_str = item['start_time_str']
    end_time_str = item['end_time_str']
    user_name = item['user_name']
    return f'{start_time_str:^7.7}-{end_time_str:^7.7} {user_name}'


def make_response_message(header, all_items):
    list_booked_time_str = '\n'.join([make_row_from_item(item)
                                      for item in all_items])

    message = header + '\n' + list_booked_time_str
    return message


def parse_time_delta(msg):
    time_regex = r'(\d{1,2}:\d{2})\s*[-,]\s*(\d{1,2}:\d{2})'
    result = re.findall(time_regex, msg)
    if len(result) >= 1:
        start_time_str, end_time_str = result[0]
        try:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            start_delta = 60*start_time.hour + start_time.minute
            end_delta = 60*end_time.hour + end_time.minute
            if start_time < end_time:
                return (start_delta, end_delta), (start_time_str, end_time_str)
        except ValueError:
            pass
    return None, None


def create_answer(db_instance, request_data):
    deltas, start_end_times_str = parse_time_delta(request_data['text'])

    answer = 'Rejected!\nInvalid time!'
    if deltas is not None:
        start_delta, end_delta = deltas
        start_time_str, end_time_str = start_end_times_str
        ITEM_IN_DB['_id'] = datetime.now().timestamp()
        ITEM_IN_DB['user_id'] = request_data['from']['id']
        ITEM_IN_DB['user_name'] = request_data['from']['name']
        ITEM_IN_DB['group_id'] = request_data['conversation']['id']
        ITEM_IN_DB['start_delta'] = start_delta
        ITEM_IN_DB['end_delta'] = end_delta
        ITEM_IN_DB['start_end_delta'] = end_delta - start_delta
        ITEM_IN_DB['start_time_str'] = start_time_str
        ITEM_IN_DB['end_time_str'] = end_time_str
        ITEM_IN_DB['tzname'] = request_data['entities'][0]['timezone']

        is_saved = db_instance.save(ITEM_IN_DB)
        if is_saved:
            header = 'Accepted!(cool)'
        else:
            header = 'Rejected!\nTime already has booked:|'
        all_items = db_instance.get_all_items(ITEM_IN_DB)

        answer = make_response_message(header, all_items)
    return answer


def message_handler(request_data, db_instance):
    local_tz_name = request_data['entities'][0]['timezone']
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
