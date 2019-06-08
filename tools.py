import logging

from datetime import datetime, timedelta
from pytz import all_timezones, reference

import re

import pymongo

from static_data import \
    QUERY_DELTA_MATCHES, \
    QUERY_DELTA_SUM, \
    QUERY_START_TIME_SUBSTRACT, \
    QUERY_ALL_ITEMS_SORT_BY_STIME, \
    ITEM_IN_DB


class DatabaseClient:

    def __init__(self, db_uri, db_name):
        self.__db_client = pymongo.MongoClient(db_uri)
        self.__db_instance = self.__db_client[db_name]
        self.__tz_store = {}
        self.__collections = {}

    def set_tz(self, item):
        group_id = item['group_id']
        tz = item['tz']
        self.__tz_store[tz] = group_id

    def is_exists(self, item):
        group_id = item['group_id']
        start_time, end_time = item['start_time'], item['end_time']
        delta = end_time - start_time

        if group_id not in self.__collections:
            self.__collections[group_id] = self.__db_instance[f'coll_{group_id[:8]}']
            self.set_tz(item)
        collection = self.__collections[group_id]

        QUERY_START_TIME_SUBSTRACT['$addFields']['start_times_sb']['$abs']['$subtract'][-1] = start_time
        QUERY_DELTA_SUM['$addFields']['deltas_sum']['$add'][-1] = delta
        items = list(collection.aggregate([QUERY_START_TIME_SUBSTRACT,
                                           QUERY_DELTA_SUM,
                                           QUERY_DELTA_MATCHES, ]))

        if len(items) > 0:
            return True
        return False

    def save(self, item):
        if not self.is_exists(item):
            self.__collections[item['group_id']].insert_one(item)
            return True
        return False

    def get_all_items(self, item):
        group_id = item['group_id']
        collection = self.__collections.get(group_id)
        if collection is not None:
            return list(collection.aggregate([QUERY_ALL_ITEMS_SORT_BY_STIME, ]))
        return []

    def delete_all_docs(self):
        for tz, group_id in self.__tz_store.items():
            utc_now = datetime.now()
            local_now = utc_now.replace(tzinfo=tz)
            if 0 <= local_now.hour < 1:
                collection = self.__collections.get(group_id)
                if collection is not None:
                    deleted = collection.delete_many({})
                    logging.warning(f'Deleted {deleted.deleted_count} items!'
                                    f'Database with timezone: {tz}')


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
    local_timestamp = request_data['localTimestamp']
    local_tz = datetime.fromisoformat(local_timestamp).tzname()
    answer = 'Rejected!\nInvalid time!'
    if start_tmsp and end_tmsp:
        ITEM_IN_DB['_id'] = datetime.now().timestamp()
        ITEM_IN_DB['user_id'] = request_data['from']['id']
        ITEM_IN_DB['user_name'] = request_data['from']['name']
        ITEM_IN_DB['group_id'] = request_data['conversation']['id']
        ITEM_IN_DB['start_time'] = start_tmsp
        ITEM_IN_DB['end_time'] = end_tmsp
        ITEM_IN_DB['delta'] = end_tmsp - start_tmsp
        ITEM_IN_DB['tz'] = local_tz

        is_saved = db_instance.save(ITEM_IN_DB)
        if is_saved:
            header = 'Accepted!(cool)'
        else:
            header = 'Rejected!\nTime already have booked:|'
        all_items = db_instance.get_all_items(ITEM_IN_DB)

        answer = make_response_message(header, all_items)
    return answer




