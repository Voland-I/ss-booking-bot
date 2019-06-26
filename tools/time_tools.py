from datetime import datetime
import re

import pytz


def parse_time_deltas(msg):
    time_regex = r'(\d{1,2}[:\.]\d{2})\s*[-,]\s*(\d{1,2}[:\.]\d{2})'
    time_result = re.findall(time_regex, msg)
    if time_result:
        return time_result[0]
    return None, None


def get_time_from_str(time_str):
    time_str = re.sub('\.', ':', time_str)
    try:
        time_ = datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        pass
    else:
        return time_
    return None


def make_time_deltas_from_str(start_time_str, end_time_str):
    if start_time_str is not None and end_time_str is not None:
        start_time = get_time_from_str(start_time_str)
        end_time = get_time_from_str(end_time_str)
        if start_time is not None and end_time is not None:
            start_delta = 60*start_time.hour + start_time.minute
            end_delta = 60*end_time.hour + end_time.minute
            if start_time < end_time:
                return start_delta, end_delta
    return None, None


def get_tzname_from_request(request_data):
    try:
        tzname = request_data['entities'][0]['timezone']
    except KeyError:
        tzname = 'UTC'

    return tzname


def get_local_now_iso(tzname):
    tz = pytz.timezone(tzname)
    local_now = datetime.now(tz=tz)
    local_now_iso = local_now.isoformat()
    return local_now_iso


def is_past(request_data, times_str):
    start_time_str, _ = times_str
    tzname = get_tzname_from_request(request_data)
    tz = pytz.timezone(tzname)
    local_time_now = datetime.now(tz=tz).time()
    start_time = get_time_from_str(start_time_str)
    if start_time < local_time_now:
        return True
    return False












