from datetime import datetime
import pytz

import logging

import pymongo

from tools.static_data import \
                        QUERY_DELTA_MATCHES, \
                        QUERY_DELTA_SUM, \
                        QUERY_START_TIME_SUBTRACT, \
                        QUERY_ALL_ITEMS_SORT_BY_STIME


class DatabaseClient:

    def __init__(self, db_uri, db_name):
        self.__db_client = pymongo.MongoClient(db_uri)
        self.__db_instance = self.__db_client[db_name]
        self.__tz_store = {}
        self.__collections = {}

    def set_tz(self, item):
        group_id = item['group_id']
        tzname = item['tzname']
        self.__tz_store[tzname] = group_id

    def is_exists(self, item):
        group_id = item['group_id']
        start_delta, end_delta = item['start_delta'], item['end_delta']
        start_end_delta = item['start_end_delta']

        if group_id not in self.__collections:
            self.__collections[group_id] = self.__db_instance[f'coll_{group_id[:8]}']
            self.set_tz(item)
        collection = self.__collections[group_id]

        QUERY_START_TIME_SUBTRACT['$addFields']['start_deltas_sb']['$abs']['$subtract'][0]['$min'][1] = start_delta
        QUERY_START_TIME_SUBTRACT['$addFields']['start_deltas_sb']['$abs']['$subtract'][1]['$max'][1] = end_delta
        QUERY_DELTA_SUM['$addFields']['deltas_sum']['$add'][-1] = start_end_delta
        items = list(collection.aggregate([QUERY_START_TIME_SUBTRACT,
                                           QUERY_DELTA_SUM,
                                           QUERY_DELTA_MATCHES, ]))

        if len(items) > 0:
            return True
        return False

    def save(self, item):
        if not self.is_exists(item):
            group_id = item['group_id']
            self.__collections[group_id].insert_one(item)
            return True
        return False

    def get_all_items(self, item):
        group_id = item['group_id']
        collection = self.__collections.get(group_id)
        if collection is not None:
            return list(collection.aggregate([QUERY_ALL_ITEMS_SORT_BY_STIME, ]))
        return []

    def delete_all_docs(self):
        for tzname, group_id in self.__tz_store.items():
            tz = pytz.timezone(tzname)
            utc_now = datetime.utcnow().astimezone(pytz.UTC)
            local_now = utc_now.astimezone(tz)
            local_now_hour = (local_now + local_now.utcoffset()).hour
            if 0 <= local_now_hour < 1:
                collection = self.__collections.get(group_id)
                if collection is not None:
                    deleted = collection.delete_many({})
                    logging.warning(f'Deleted {deleted.deleted_count} items!'
                                    f'Database with timezone: {tzname}')
