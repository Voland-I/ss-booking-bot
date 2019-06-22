import logging
import requests

from tools.system_tools import get_value_from_env


class SkypeBot:
    
    def __init__(self):

        self._bot_name = get_value_from_env('BOT_NAME')
        self._service_uri = get_value_from_env('SERVICE_URI')
        self._token = None
        self._set_token_attempts = 5

    def _set_token(self):
        i = 0
        while (self._token is None) and (i <= self._set_token_attempts):
            i += 1
            client_id = get_value_from_env('APP_ID')
            client_secret = get_value_from_env('APP_PASSWORD')

            url = get_value_from_env('BOT_CON_AUTH_URI')
            payload_workpiece = get_value_from_env('BOT_CON_PAYLOAD_WORKPIECE')
            payload = payload_workpiece.format(client_id=client_id,
                                           client_secret=client_secret)
            headers = {'Content-Type': 'application/x-www-form-urlencoded', }
            r = requests.post(url, headers=headers, data=payload)
            r_data = r.json()
            self._token = r_data.get('access_token')

    @property
    def name(self):
        return self._bot_name

    def fake_request(self):
        requests.get(self._service_uri)

    def send_message(self, payload):
        service = payload['serviceUrl']
        conversation_id = payload['conversation']['id']
        activity_id = payload["replyToId"]

        url_workpiece = get_value_from_env('CONVERSATION_ENDP_WORKPIECE')
        if url_workpiece is not None:
            url = url_workpiece.format(service=service,
                                       conversation_id=conversation_id,
                                       activity_id=activity_id)

            self._set_token()
            auth_token = 'Bearer {0}'.format(self._token)
            headers = {
                'Authorization': auth_token,
                'Content-Type': 'Application/json',
            }

            r = requests.post(url, headers=headers, json=payload)

            if 400 <= r.status_code <= 599:
                logging.error(f'error: {r.text}')
        else:
            logging.error('Environment error! No conversation endpoint!')
