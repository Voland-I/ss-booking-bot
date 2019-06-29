from tools.time_tools import (get_local_now_iso,
                             get_tzname_from_request,
                             parse_time_deltas,
                             make_time_deltas_from_str,
                             is_past,
                             get_game_status)

from tools.static_data import GAME_STATUSES, HEADERS


def make_message_text(header, all_items):
    message_rows_list = []
    for row_number, item in enumerate(all_items, start=1):
        start_time_str = item['start_time_str']
        end_time_str = item['end_time_str']
        user_name = item['user_name']
        row = f'{row_number}.{start_time_str}-{end_time_str} {user_name}-{get_game_status(item, GAME_STATUSES)} \n'
        message_rows_list.append(row)

    text_message = ''.join(message_rows_list)
    print(text_message, 'text message')
    # text_message = header + text_message

    return text_message


def create_activity_object(request_data, response_msg, local_now_iso):
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
        'text': response_msg,
    }

    return response_object


def create_response_object_for_user(request_data, response_msg, local_now_iso):
    activity_object = create_activity_object(request_data, response_msg, local_now_iso)
    response_object = {
        'bot': {
            'id': request_data['recipient']['id'],
            'name': request_data['recipient']['id']
        },
        'isGroup': 'false',
        'members': [
            {
                'id': request_data['from']['id'],
                'name': request_data['from']['name']
            },
        ],
        'topicName': 'Answer for your action',
        'activity': activity_object
        }

    return response_object


def message_processing(db_instance, cp_instance, request_data):
    tzname = get_tzname_from_request(request_data)
    local_now_iso = get_local_now_iso(tzname)

    request_message = request_data['text']
    time_strings = parse_time_deltas(request_message)
    time_deltas = make_time_deltas_from_str(*time_strings)

    response_message = HEADERS['incorrect_enter']
    if all(time_deltas) and not is_past(request_data, time_strings):
        response_message = booking_processing(db_instance,
                                              time_deltas,
                                              time_strings,
                                              request_data)

    command_name, command_entity = cp_instance.parse_command(request_message)
    if all((command_name, command_entity)):
        response_message = cp_instance.process_command(command_name,
                                                       command_entity,
                                                       request_data=request_data)

    response_object = create_activity_object(request_data,
                                             response_message,
                                             local_now_iso)
    return response_object


def booking_processing(db_instance, time_deltas, time_strings, request_data):
    group_id = request_data['conversation']['id']

    header = HEADERS['time_booked']
    db_item = db_instance.create_item((time_deltas, time_strings), request_data)
    if not db_instance.is_exists(db_item):
        header = HEADERS['accepted']
        db_instance.save(db_item)
    all_items_in_collection = db_instance.get_all_items(group_id)
    response_message = make_message_text(header, all_items_in_collection)

    return response_message
