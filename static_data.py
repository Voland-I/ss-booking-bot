

MESSAGE_WORKPIECE = {
                    'serviceUrl': '',
                    'type': '',
                    'from': {
                        'id': '',
                        'name': ''
                    },
                    'conversation': {
                        'id': ''
                },
                'recipient': {
                        'id': '',
                        'name': ''
                    },
                    'text': '',
                    'replyToId': '',
                }

QUERY_START_TIME_SUBSTRACT = {
            '$addFields': {
                'start_times_sb': {
                    '$abs': {
                        '$subtract': ['$start_time', 0]
                    }
                }
            }
        }

QUERY_DELTA_SUM = {
    '$addFields': {
        'deltas_sum': {
            '$add': ['$delta', 0]
        }
    }
}

QUERY_DELTA_MATCHES = {
    '$match': {
            '$expr': {
                '$lte': ['$start_times_sb', '$deltas_sum']
            }
    }
}

QUERY_ALL_ITEMS_SORT_BY_STIME = {
    '$sort': {'start_time': 1},
}

ITEM_IN_DB = {
        '_id': r'datetime.now().timestamp()',
        'user_id': r'request_data["from"]["id"]',
        'user_name': r'request_data["from"]["name"]',
        'group_id': r'request_data["conversation"]["id"]',
        'start_time': r'start_tmsp',
        'end_time': r'end_tmsp',
        'delta': r'end_tmsp - start_tmsp',
        'tz': r'local_tz'
}
