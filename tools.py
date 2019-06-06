from sys import stdout

import logging

from datetime import datetime, timedelta

import re

import pymongo


logger = logging.basicConfig(filename='bbot.log',
                             level=logging.DEBUG,
                             format='%(levelname)s:%(message)s')


class DatabaseClient:

    def __init__(self, db_uri, db_name, collection_name):
        self.__db_client = pymongo.MongoClient(db_uri)
        self.__db_instance = self.__db_client[db_name]
        self.__collection = self.__db_instance[collection_name]

    def is_exists(self, document):
        time_to_reserve = document['start_time'], document['end_time']
        for item in self.get_all_items():
            time_reserved = item['start_time'], item['end_time']
            time_deltas = get_time_deltas(time_to_reserve, time_reserved)
            deltas_upper_zero = len([d for d in time_deltas if d > 0])
            deltas_lower_zero = len([d for d in time_deltas if d < 0])
            stdout.flush()
            if abs(deltas_upper_zero - deltas_lower_zero) != len(time_deltas):
                return True
        return False

    def save(self, document):
        if not self.is_exists(document):
            self.__collection.insert_one(document)
            return True
        return False

    def get_all_items(self):
        return list(self.__collection.find())

    def delete_all_docs(self):
        now = datetime.now()
        if 0 <= now.hour < 1:
            deleted = self.__collection.delete_many({})
            logger.warning(f'Deleted {deleted.deleted_count} items!')


def get_time_deltas(time_to_reserve, time_reserved):
    start_time, end_time = time_to_reserve
    res_start, res_end = time_reserved

    delta1 = res_start - start_time
    delta2 = res_end - end_time
    delta3 = res_end - start_time
    delta4 = res_start - end_time

    return delta1, delta2, delta3, delta4


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


def parse_time_from_msg(str_time):
    time_regex = r'(\d{1,2}:\d{1,2})\s*[-,]\s*(\d{1,2}:\d{1,2})'
    result = re.findall(time_regex, str_time)
    if len(result) >= 1:
        today = datetime.today()
        start_time_str, end_time_str = result[0]
        try:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            start_tmsp = datetime.combine(today, start_time).timestamp()
            end_tmsp = datetime.combine(today, end_time).timestamp()
            if start_time < end_time:
                return start_tmsp, end_tmsp
        except ValueError:
            pass
    return None, None


def create_answer(db_instance, request_data):
    start_tmsp, end_tmsp = parse_time_from_msg(request_data['text'])
    if start_tmsp and end_tmsp:
        data = {
            '_id': datetime.now().timestamp(),
            'user_id': request_data['from']['id'],
            'user_name': request_data['from']['name'],
            'group_id': request_data['conversation']['id'],
            'start_time': start_tmsp,
            'end_time': end_tmsp
        }

        if not db_instance.is_exists(data):
            header = 'Accepted!(cool)'
            db_instance.save(data)
        else:
            header = 'Rejected! Time already have booked:|'
        all_items = sorted(
            db_instance.get_all_items(), key=lambda itm: itm['start_time']
        )

        answer = make_response_message(header, all_items)
        return answer
    return




