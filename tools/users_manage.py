from tools.time_tools import get_value_from_data_object, get_local_now_time
from tools.message_processing import create_response_object_for_user
from tools.static_data import MESSAGES


def conversation_update_processing(db_instance, request_data):
    members_added = get_value_from_data_object(request_data,
                                               ('membersAdded', ),
                                               default_value=[])

    bot_name = get_value_from_data_object(request_data,
                                          ('recipient', 'name'))

    group_id = get_value_from_data_object(request_data,
                                          ('conversation', 'id'))

    tzname = get_value_from_data_object(request_data,
                                        ('entities', 0, 'timezone'),
                                        default_value='UTC')

    local_now_iso = get_local_now_time(tzname)
    for member in members_added:
        if member['name'] == bot_name:
            db_instance.set_collection_and_tzname_if_not_exist(group_id, tzname)
            response_message = get_value_from_data_object(MESSAGES,
                                                          ('welcome', ))

            response_object = create_response_object_for_user(request_data,
                                                              response_message,
                                                              local_now_iso)

            return response_object
