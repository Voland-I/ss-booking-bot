from datetime import datetime
import logging

import pytz
import pymongo

from tools.time_tools import get_tzname_from_request


class DatabaseClient:

    def __init__(self, db_uri, db_name):
        self._db_client = pymongo.MongoClient(db_uri)
        self._db_instance = self._db_client[db_name]
        self._tz_store = {}
        self._collections = {}

    def _set_group(self, group_id):
        self._collections[group_id] = self._db_instance[f'coll_{group_id[:8]}']

    def _set_tz(self, group_id, tzname):
        self._tz_store[group_id] = tzname

    @staticmethod
    def create_item(parsed_time, request_data):
        deltas, start_end_times_str = parsed_time
        start_delta, end_delta = deltas
        start_time_str, end_time_str = start_end_times_str
        tzname = get_tzname_from_request(request_data)
        db_item = {
            'user_id': request_data['from']['id'],
            'user_name': request_data['from']['name'],
            'group_id': request_data['conversation']['id'],
            'start_delta': start_delta,
            'end_delta': end_delta,
            'start_end_delta': end_delta - start_delta,
            'start_time_str': start_time_str,
            'end_time_str': end_time_str,
            'tzname': tzname
        }

        return db_item

    @staticmethod
    def _get_start_end_deltas_subtract(start_delta, end_delta):
        query = {
            '$addFields': {
                'start_deltas_sb': {
                    '$abs': {
                        '$subtract': [{
                            '$min': ['$start_delta', start_delta]
                        },
                        {
                            '$max': ['$end_delta', end_delta]
                         }]
                    }
                }
            }
        }

        return query

    @staticmethod
    def _get_deltas_sum(start_end_delta):
        query = {
            '$addFields': {
                'deltas_sum': {
                    '$add': ['$start_end_delta', start_end_delta]
                }
            }
        }

        return query

    @staticmethod
    def _get_deltas_matches():
        query = {
            '$match': {
                '$expr': {
                    '$lte': ['$start_deltas_sb', '$deltas_sum']
                }
            }
        }

        return query

    @staticmethod
    def _get_all_items_sorted_by_time():
        query = {
            '$sort': {'start_delta': 1},
        }

        return query

    def is_exists(self, item):
        group_id = item['group_id']
        start_delta, end_delta = item['start_delta'], item['end_delta']
        start_end_delta = item['start_end_delta']

        collection = self._collections[group_id]

        # todo: make row for queries and format args into it
        deltas_subtract_query = self._get_start_end_deltas_subtract(start_delta,
                                                                    end_delta)
        deltas_sum_query = self._get_deltas_sum(start_end_delta)
        deltas_matches_query = self._get_deltas_matches()

        queries_pipeline = [
            deltas_subtract_query,
            deltas_sum_query,
            deltas_matches_query,
        ]
        items = list(collection.aggregate(queries_pipeline))

        if items:
            return True
        return False

    def set_collection_and_tzname_if_not_exist(self, group_id, tzname):
        if group_id not in self._collections:
            self._set_group(group_id)
        if group_id not in self._tz_store:
            self._set_tz(group_id, tzname)

    def save(self, item):
        group_id = item['group_id']
        self._collections[group_id].insert_one(item)

    def get_all_items(self, group_id):
        collection = self._collections[group_id]
        sort_by_start_time_query = self._get_all_items_sorted_by_time()
        queries_pipeline = [sort_by_start_time_query, ]
        return list(collection.aggregate(queries_pipeline))

    def delete_all_docs(self):
        for group_id, tzname in self._tz_store.items():
            tz = pytz.timezone(tzname)
            utc_now = datetime.utcnow()
            local_now = utc_now.astimezone(tz)
            local_now_hour = (local_now + local_now.utcoffset()).hour
            if 0 <= local_now_hour < 1:
                collection = self._collections.get(group_id)
                if collection is not None:
                    deleted = collection.delete_many({})
                    logging.warning(f'Deleted {deleted.deleted_count} items!'
                                    f'Database with timezone: {tzname}')

