from datetime import datetime

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

        QUERY_START_TIME_SUBTRACT['$addFields']['start_times_sb']['$abs']['$subtract'][0]['$min'][1] = start_time
        QUERY_START_TIME_SUBTRACT['$addFields']['start_times_sb']['$abs']['$subtract'][1]['$max'][1] = end_time
        QUERY_DELTA_SUM['$addFields']['deltas_sum']['$add'][-1] = delta
        items = list(collection.aggregate([QUERY_START_TIME_SUBTRACT,
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
