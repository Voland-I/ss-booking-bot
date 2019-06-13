from datetime import datetime
import pytz

import re

from tools.static_data import ITEM_IN_DB


def get_now_local_datetime(request_data):
    tz_from_request_name = request_data['entities'][0]['timezone']
    tz_from_request = pytz.timezone(tz_from_request_name)
    now_utc = datetime.utcnow().astimezone(pytz.UTC)
    now_local = now_utc.astimezone(tz_from_request)
    return now_local


def make_row_from_item(item):
    start_time_str = datetime.fromtimestamp(item['start_time']).strftime('%H:%M')
    end_time_str = datetime.fromtimestamp(item['end_time']).strftime('%H:%M')
    user_name = item['user_name']
    return f'{start_time_str:^7.7}-{end_time_str:^7.7} {user_name}'


def make_response_message(header, all_items):
    list_booked_time_str = '\n'.join([make_row_from_item(item)
                                      for item in all_items])

    message = header + '\n' + list_booked_time_str
    return message


def parse_time_from_msg(msg, tz):
    time_regex = r'(\d{1,2}:\d{1,2})\s*[-,]\s*(\d{1,2}:\d{1,2})'
    result = re.findall(time_regex, msg)
    utc_now = datetime.utcnow()
    local_now = utc_now.astimezone(tz)
    if len(result) >= 1:
        start_time_str, end_time_str = result[0]
        try:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            start_tmsp = datetime.combine(local_now, start_time).timestamp()
            end_tmsp = datetime.combine(local_now, end_time).timestamp()
            if start_time < end_time:
                return int(start_tmsp), int(end_tmsp)
        except ValueError:
            pass
    return None, None


def create_answer(db_instance, request_data):
    request_data_local_tz_name = request_data['entities'][0]['timezone']
    request_data_local_tz = pytz.timezone(request_data_local_tz_name)
    start_tmsp, end_tmsp = parse_time_from_msg(
        request_data['text'], request_data_local_tz
    )

    answer = 'Rejected!\nInvalid time!'
    if start_tmsp and end_tmsp:
        ITEM_IN_DB['_id'] = datetime.now().timestamp()
        ITEM_IN_DB['user_id'] = request_data['from']['id']
        ITEM_IN_DB['user_name'] = request_data['from']['name']
        ITEM_IN_DB['group_id'] = request_data['conversation']['id']
        ITEM_IN_DB['start_time'] = start_tmsp
        ITEM_IN_DB['end_time'] = end_tmsp
        ITEM_IN_DB['delta'] = end_tmsp - start_tmsp
        ITEM_IN_DB['tzname'] = request_data_local_tz_name

        is_saved = db_instance.save(ITEM_IN_DB)
        if is_saved:
            header = 'Accepted!(cool)'
        else:
            header = 'Rejected!\nTime already have booked:|'
        all_items = db_instance.get_all_items(ITEM_IN_DB)

        answer = make_response_message(header, all_items)
    return answer
