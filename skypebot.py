import os

import logging

import requests
import threading
import time


class SkypeBot:
    
    def __init__(self, client_id, client_secret):

        def get_token():
            global token

            url = os.environ.get('BOT_CON_AUTH_URI')
            payload_workpiece = os.environ.get('BOT_CON_PAYLOAD_WORKPIECE')
            payload = payload_workpiece.format(client_id=client_id,
                                               client_secret=client_secret)

            headers = {'Content-Type': 'application/x-www-form-urlencoded', }
            response = requests.post(url, headers=headers, data=payload)

            data = response.json()
            token = data.get('access_token')

        def run_it():
            while True:
                get_token()
                time.sleep(3590)

        self.t = threading.Thread(target=run_it, name='thread_get_token')
        self.t.daemon = True
        self.t.start()

    @staticmethod
    def send_message(payload):
        service = payload['serviceUrl']
        conversation_id = payload['conversation']['id']
        activity_id = payload["replyToId"]

        url_workpiece = os.environ.get('CONVERSATION_ENDP_WORKPIECE')
        if url_workpiece is not None:
            url = url_workpiece.format(service=service,
                                       conversation_id=conversation_id,
                                       activity_id=activity_id)

            auth_token = 'Bearer {0}'.format(token)
            headers = {'Authorization': auth_token,
                       'Content-Type': 'Application/json', }

            r = requests.post(url, headers=headers, json=payload)

            if 400 <= r.status_code <= 599:
                logging.error(f'error: {r.text}')
        else:
            logging.error('Environment error! No conversation endpoint!')
