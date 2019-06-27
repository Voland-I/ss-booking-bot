from tools.system_tools import get_value_from_env
from tools.time_tools import get_tzname_from_request, get_local_now_iso
from tools.message_processing import create_response_object_for_user
from tools.static_data import MESSAGES


def conversation_update_processing(db_instance, request_data):
    members_added = request_data.get('membersAdded')
    bot_name = request_data['recipient']['name']
    group_id = request_data['conversation']['id']
    tzname = get_tzname_from_request(request_data)
    local_now_iso = get_local_now_iso(tzname)
    if members_added is not None:
        for member in members_added:
            if member['name'] == bot_name:
                db_instance.set_collection_and_tzname_if_not_exist(group_id, tzname)
                response_message = MESSAGES['welcome']

                response_object = create_response_object_for_user(request_data,
                                                         response_message,
                                                         local_now_iso)

                return response_object
