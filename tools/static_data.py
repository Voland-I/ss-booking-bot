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

