from datetime import datetime
import re

import pytz

from tools.data_handling import get_value_from_data_object


def parse_time_deltas(msg):
    time_regex = r'(\d{1,2}[:\.]\d{2})\s*[-,]\s*(\d{1,2}[:\.]\d{2})'
    time_result = re.findall(time_regex, msg)
    if time_result:
        time_str = time_result[0]
        start_time_str, end_time_str = time_str
        start_time_str = re.sub('\.', ':', start_time_str)
        end_time_str = re.sub('\.', ':', end_time_str)
        return start_time_str, end_time_str
    return None, None


def get_time_from_str(time_str):
    try:
        time_ = datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        pass
    else:
        return time_
    return None


def get_delta(time_):
    if isinstance(time_, str):
        time_ = get_time_from_str(time_)
    if time_ is not None:
        delta = 60*time_.hour + time_.minute
        return delta
    return None


def make_time_deltas_from_str(start_time_str, end_time_str):
    if start_time_str is not None and end_time_str is not None:
        start_delta = get_delta(start_time_str)
        end_delta = get_delta(end_time_str)
        if all((start_delta, end_delta)) and (start_delta < end_delta):
            return start_delta, end_delta
    return None, None


def get_local_now_time(tzname):
    tz = pytz.timezone(tzname)
    local_now = datetime.now(tz=tz)
    return local_now.time()


def is_past(request_data, times_str):
    start_time_str, _ = times_str
    tzname = get_value_from_data_object(request_data,
                                        ('entities', 0, 'timezone'),
                                        'UTC')

    local_now = get_local_now_time(tzname)
    start_time = get_time_from_str(start_time_str)
    if start_time < local_now:
        return True
    return False


def get_game_status(item, statuses):
    tzname = get_value_from_data_object(item, ('tzname', ), default_value='UTC')
    start_delta = get_value_from_data_object(item, ('start_delta', ))
    end_delta = get_value_from_data_object(item, ('end_delta', ))

    local_now = get_local_now_time(tzname)
    now_delta = get_delta(local_now)

    game_status = get_value_from_data_object(statuses, ('will_be', ))

    if start_delta <= now_delta <= end_delta:
        game_status = statuses['in_process']
    if end_delta < now_delta:
        game_status = statuses['played']

    return game_status










