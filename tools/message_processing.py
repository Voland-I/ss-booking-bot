from datetime import datetime
import re

import pytz


def make_response_message_text(header, all_items):
    message_rows_list = [header, ]
    for item in all_items:
        start_time_str = item['start_time_str']
        end_time_str = item['end_time_str']
        user_name = item['user_name']
        row = f'{start_time_str:^7.7}-{end_time_str:^7.7} {user_name}'
        message_rows_list.append(row)

    text_message = '\n'.join([row for row in message_rows_list])

    return text_message


def parse_time_delta(msg):
    time_regex = r'(\d{1,2}:\d{2})\s*[-,]\s*(\d{1,2}:\d{2})'
    result = re.findall(time_regex, msg)
    if result:
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


def create_db_item(parsed_time, request_data):
    deltas, start_end_times_str = parsed_time
    start_delta, end_delta = deltas
    start_time_str, end_time_str = start_end_times_str

    tzname = request_data['endtities'][0]['timezone']

    db_item = {
        'user_id': request_data['from']['id'],
        'user_name': request_data['from']['name'],
        'group_id': request_data['conversation']['id'],
        'start_delta': start_delta,
        'end_delta': end_delta,
        'start_end_delta': end_delta - start_delta,
        'start_time_str': start_time_str,
        'end_time_str': end_time_str,
        'tzname': tzname
    }

    return db_item


def get_local_now_iso(tzname):
    tz = pytz.timezone(tzname)
    local_now = datetime.now(tz=tz)
    local_now_iso = local_now.isoformat()
    return local_now_iso


def create_message_response_object(request_data, answer, local_now_iso):
    response_object = {
        'serviceUrl': request_data['serviceUrl'],
        'type': request_data['type'],
        'from': {
            'id': request_data['recipient']['id'],
            'name': request_data['recipient']['name']
        },
        'recipient': {
            'id': request_data['from']['id'],
            'name': request_data['from']['name']
        },
        'conversation': {
            'id': request_data['conversation']['id']
        },
        'replyToId': request_data['id'],
        'timestamp': local_now_iso,
        'text': answer
    }

    return response_object


def get_response_message(db_instance, request_data):
    request_message = request_data['text']
    try:
        timezone_name = request_data['entities'][0]['timezone']
    except KeyError:
        timezone_name = 'UTC'

    local_now_iso = get_local_now_iso(timezone_name)
    all_items_in_collection = []

    header = 'Rejected!\nInvalid time!'
    time_deltas, time_string = parse_time_delta(request_message)
    if time_deltas is not None:
        header = 'Rejected! Time already booked!'
        db_item = create_db_item((time_deltas, time_string), request_data)
        if db_instance.is_exists(db_item):
            header = 'Accepted!'
            db_instance.save(db_item)
        all_items_in_collection = db_instance.get_all_items(db_item)
    response_message = make_response_message_text(header,
                                                  all_items_in_collection)

    response_object = create_message_response_object(request_data,
                                                     response_message,
                                                     local_now_iso)

    return response_object






















