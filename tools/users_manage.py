from tools.system_tools import get_value_from_env
from tools.time_tools import get_tzname_from_request, get_local_now_iso
from tools.message_processing import create_response_object


_WELCOME_MESSAGE = '''
Hi all!\n
To see all available commands type help!
'''


def conversation_update_processing(db_instance, request_data):
    members_added = request_data.get('membersAdded')
    bot_name = get_value_from_env('BOT_NAME')
    group_id = request_data['conversation']['id']
    tzname = get_tzname_from_request(request_data)
    local_now_iso = get_local_now_iso(tzname)
    if members_added is not None:
        for member in members_added:
            if member['name'] == bot_name:
                db_instance.set_tz(group_id, tzname)
                response_message = _WELCOME_MESSAGE

                response_object = create_response_object(request_data,
                                                         response_message,
                                                         local_now_iso)

                return response_object
