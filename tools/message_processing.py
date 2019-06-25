from tools.time_tools import get_local_now_iso, \
                             get_tzname_from_request, \
                             parse_time_deltas, \
                             make_time_deltas_from_str


def make_message_text(header, all_items):
    message_rows_list = [header, ]
    for item in all_items:
        start_time_str = item['start_time_str']
        end_time_str = item['end_time_str']
        user_name = item['user_name']
        row = f'{start_time_str: ^7.7}-{end_time_str: ^7.7} {user_name}'
        message_rows_list.append(row)

    text_message = '\n'.join([row for row in message_rows_list])

    return text_message


def create_response_object(request_data, response_msg, local_now_iso):
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
        'text': response_msg
    }

    return response_object


def message_processing(db_instance, cp_instance, request_data):
    tzname = get_tzname_from_request(request_data)
    local_now_iso = get_local_now_iso(tzname)

    request_message = request_data['text']
    group_id = request_data['conversation']['id']
    time_strings = parse_time_deltas(request_message)
    time_deltas = make_time_deltas_from_str(*time_strings)

    response_message = 'Incorrect time or command:|'
    if all(time_deltas):
        response_message = booking_processing(db_instance,
                                              time_deltas,
                                              time_strings,
                                              request_data)

    command = cp_instance.parse_command(request_message)
    if command:
        response_message = cp_instance.process_command(command,
                                                       group_id=group_id)

    response_object = create_response_object(request_data,
                                             response_message,
                                             local_now_iso)
    return response_object


def booking_processing(db_instance, time_deltas, time_strings, request_data):
    group_id = request_data['conversation']['id']

    header = 'Rejected! Time already booked!'
    db_item = db_instance.create_item((time_deltas, time_strings), request_data)
    if not db_instance.is_exists(db_item):
        header = 'Accepted!'
        db_instance.save(db_item)
    all_items_in_collection = db_instance.get_all_items(group_id)
    response_message = make_message_text(header, all_items_in_collection)

    return response_message
