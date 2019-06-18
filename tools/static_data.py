MESSAGE = {
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

QUERY_START_TIME_SUBTRACT = {
            '$addFields': {
                'start_deltas_sb': {
                    '$abs': {
                        '$subtract': [{
                            '$min': ['$start_delta', 'start_delta_item']
                        },
                        {
                            '$max': ['$end_delta', 'end_delta_item']
                         }]
                    }
                }
            }
        }

QUERY_DELTA_SUM = {
    '$addFields': {
        'deltas_sum': {
            '$add': ['$start_end_delta', 0]
        }
    }
}

QUERY_DELTA_MATCHES = {
    '$match': {
            '$expr': {
                '$lte': ['$start_deltas_sb', '$deltas_sum']
            }
    }
}

QUERY_ALL_ITEMS_SORT_BY_STIME = {
    '$sort': {'start_delta': 1},
}

ITEM_IN_DB = {
        '_id': r'datetime.now().timestamp()',
        'user_id': r'request_data["from"]["id"]',
        'user_name': r'request_data["from"]["name"]',
        'group_id': r'request_data["conversation"]["id"]',
        'start_delta': r'start_delta',
        'end_delta': r'end_delta',
        'start_end_delta': r'end_delta - start_delta',
        'start_time_str': '',
        'end_time_str': '',
        'tzname': ''
}
