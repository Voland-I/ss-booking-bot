from datetime import datetime
import logging

import pytz
import pymongo

from tools.static_data import (QUERY_DELTA_MATCHES,
                               QUERY_DELTA_SUM,
                               QUERY_START_TIME_SUBTRACT,
                               QUERY_ALL_ITEMS_SORT_BY_STIME)


class DatabaseClient:

    def __init__(self, db_uri, db_name):
        self._db_client = pymongo.MongoClient(db_uri)
        self._db_instance = self._db_client[db_name]
        self._tz_store = {}
        self._collections = {}

    def set_tz(self, item):
        group_id = item['group_id']
        tzname = item['tzname']
        self._tz_store[tzname] = group_id

    def is_exists(self, item):
        group_id = item['group_id']
        start_delta, end_delta = item['start_delta'], item['end_delta']
        start_end_delta = item['start_end_delta']

        if group_id not in self._collections:
            self._collections[group_id] = \
                self._db_instance[f'coll_{group_id[:8]}']
            self.set_tz(item)

        collection = self._collections[group_id]

        # todo: make row for queries and format args into it
        QUERY_START_TIME_SUBTRACT['$addFields']['start_deltas_sb']['$abs']['$subtract'][0]['$min'][1] = start_delta
        QUERY_START_TIME_SUBTRACT['$addFields']['start_deltas_sb']['$abs']['$subtract'][1]['$max'][1] = end_delta
        QUERY_DELTA_SUM['$addFields']['deltas_sum']['$add'][-1] = start_end_delta

        query_pipeline = [
            QUERY_START_TIME_SUBTRACT,
            QUERY_DELTA_SUM,
            QUERY_DELTA_MATCHES,
        ]
        items = list(collection.aggregate(query_pipeline))

        if items:
            return True
        return False

    def save(self, item):
        group_id = item['group_id']
        self._collections[group_id].insert_one(item)

    def get_all_items(self, item):
        group_id = item['group_id']
        collection = self._collections.get(group_id)
        if collection is not None:
            query_pipeline = [QUERY_ALL_ITEMS_SORT_BY_STIME, ]
            return list(collection.aggregate(query_pipeline))
        return []

    def delete_all_docs(self):
        for tzname, group_id in self._tz_store.items():
            tz = pytz.timezone(tzname)
            utc_now = datetime.utcnow().astimezone(pytz.UTC)
            local_now = utc_now.astimezone(tz)
            local_now_hour = (local_now + local_now.utcoffset()).hour
            if 0 <= local_now_hour < 1:
                collection = self._collections.get(group_id)
                if collection is not None:
                    deleted = collection.delete_many({})
                    logging.warning(f'Deleted {deleted.deleted_count} items!'
                                    f'Database with timezone: {tzname}')

