import sys
from os import getcwd

from datetime import datetime, timedelta
from tzlocal import get_localzone
import pytz

import unittest
from unittest import mock

sys.path.insert(0, getcwd())

from tools.message_handlers import get_now_local_datetime, \
                                   make_row_from_item, \
                                   make_response_message, \
                                   parse_time_from_msg, \
                                   create_answer


class TestGetNowLocalDatetime(unittest.TestCase):

    DATA_STUB = {
        'entities': [{
            'timezone': ''
        }]
    }

    def setUp(self):
        self.UTC = pytz.UTC
        self.local_tz = get_localzone()

        self.utc_now = datetime.utcnow()
        self.utc_now = self.utc_now.astimezone(self.UTC)

        self.local_now = self.utc_now.astimezone(self.local_tz)
        self.local_now_tmsp = self.local_now.timestamp()
        self.local_now_str = self.local_now.isoformat()

        self.DATA_STUB['entities'][0]['timezone'] = self.local_tz.zone

    @mock.patch('tools.message_handlers.datetime')
    def test_correct_local_time(self, dt_mock):
        dt_mock.utcnow.return_value = self.utc_now

        result = get_now_local_datetime(self.DATA_STUB)

        self.assertEqual(result, self.local_now)


class TestMakeRowFromItem(unittest.TestCase):

    def setUp(self):
        utcnow = datetime.utcnow()
        delta = timedelta(hours=1)
        self.UTC = pytz.UTC
        self.local_tz = get_localzone()
        self.utc_now = utcnow.astimezone(self.UTC)

        self.start_time = self.utc_now.astimezone(self.local_tz)
        self.end_time = (self.utc_now + delta).astimezone(self.local_tz)

        self.start_time_tmsp = self.start_time.timestamp()
        self.end_time_tmsp = self.end_time.timestamp()

        self.item_stub = {
            'start_time': self.start_time_tmsp,
            'end_time': self.end_time_tmsp,
            'user_name': 'test_user',
        }

    def test_make_row_from_item(self):
        control_start_time_str = self.start_time.strftime('%H:%M')
        control_end_time_str = self.end_time.strftime('%H:%M')

        result_row = make_row_from_item(self.item_stub)

        self.assertIn(control_start_time_str, result_row)
        self.assertIn(control_end_time_str, result_row)
        self.assertIn(self.item_stub['user_name'], result_row)


class TestMakeResponseMessage(unittest.TestCase):

    HEADER_TEST = 'Test Header!(cool)'

    def setUp(self):
        utcnow = datetime.utcnow()
        self.UTC = pytz.UTC
        self.local_tz = get_localzone()
        self.utc_now = utcnow.astimezone(self.UTC)

        self.items = []

        game_time_delta = timedelta(minutes=30)
        interval = game_time_delta + timedelta(minutes=10)

        self.make_row_from_item_mock = lambda itm: \
            f'{itm["start_time_str"]}-{itm["end_time_str"]}-{itm["user_name"]}'

        for i in range(4):
            start_time_utc = self.utc_now + i*interval
            end_time_utc = self.utc_now + i*interval + game_time_delta
            start_time = start_time_utc.astimezone(self.local_tz)
            end_time = end_time_utc.astimezone(self.local_tz)
            user_name = f'test_user{i}'
            item = {
                'start_time': start_time.timestamp(),
                'end_time': end_time.timestamp(),
                'start_time_str': start_time.strftime('%H:%M'),
                'end_time_str': end_time.strftime('%H:%M'),
                'user_name': user_name
            }

            self.items.append(item)

    @mock.patch('tools.message_handlers.make_row_from_item')
    def test_how_many_times_make_row_from_item_was_called(self, make_row_mock):

        make_row_mock.side_effect = self.make_row_from_item_mock
        make_response_message(self.HEADER_TEST, self.items)

        self.assertEqual(make_row_mock.call_count, len(self.items))

    @mock.patch('tools.message_handlers.make_row_from_item')
    def test_with_what_args_make_row_from_item_was_called(self, make_row_mock):
        make_row_mock.side_effect = self.make_row_from_item_mock

        make_response_message(self.HEADER_TEST, self.items)

        call_args_list = [c_o[0][0] for c_o in make_row_mock.call_args_list]

        self.assertListEqual(call_args_list, self.items)

    def test_header_and_all_items_in_message(self):
        ravel_items = []
        for item in self.items:
            ravel_items.extend((item['start_time_str'],
                                item['end_time_str'],
                                item['user_name']))

        result = make_response_message(self.HEADER_TEST, self.items)

        for item in ravel_items:
            self.assertIn(item, result)


class TestParseTimeFromMsg(unittest.TestCase):

    def setUp(self):
        utcnow = datetime.utcnow()
        delta = timedelta(minutes=30)
        self.UTC = pytz.UTC
        self.local_tz = get_localzone()
        self.utc_now = utcnow.astimezone(self.UTC)
        self.local_now = self.utc_now.astimezone(self.local_tz)
        self.end_time = (self.utc_now + delta).astimezone(self.local_tz)
        self.time_items = {}
        self.time_items['correct'] = {
            'start_time': self.local_now.timestamp(),
            'end_time': self.end_time.timestamp(),
            'start_time_str': self.local_now.strftime('%H:%M'),
            'end_time_str': self.end_time.strftime('%H:%M')

        }

        self.time_items['incorrect_format'] = {
            'start_time': self.local_now.timestamp(),
            'end_time': self.end_time.timestamp(),
            'start_time_str': self.local_now.strftime('%H-%M'),
            'end_time_str': self.end_time.strftime('%H-%M')
        }

    @mock.patch('tools.message_handlers.datetime')
    def test_with_correct_time_input(self, dt_mock):
        start_time_str = self.time_items['correct']['start_time_str']
        start_time_check = datetime.strptime(start_time_str, '%H:%M').time()
        start_tmsp_check = datetime.combine(self.local_now, start_time_check).timestamp()

        end_time_str = self.time_items['correct']['end_time_str']
        end_time_check = datetime.strptime(end_time_str, '%H:%M').time()
        end_tmsp_check = datetime.combine(self.local_now, end_time_check).timestamp()
        test_msg = f'Please, book me time: {start_time_str}-{end_time_str}'

        dt_mock.utcnow.return_value = self.utc_now
        dt_mock.strptime.side_effect = lambda dt, f: datetime.strptime(dt, f)
        dt_mock.combine.side_effect = lambda lt, gt: datetime.combine(lt, gt)

        result = parse_time_from_msg(test_msg, self.local_tz)

        self.assertTupleEqual(result, (start_tmsp_check, end_tmsp_check))

    def test_start_time_grater_than_end_time(self):
        start_time_str = self.time_items['correct']['end_time_str']
        end_time_str = self.time_items['correct']['start_time_str']
        test_msg = f'incorrect time interval {start_time_str}-{end_time_str}'

        result = parse_time_from_msg(test_msg, self.local_tz)

        self.assertEqual(result, (None, None))

    def test_incorrect_time_format(self):
        start_time_str = self.time_items['incorrect_format']['start_time_str']
        end_time_str = self.time_items['incorrect_format']['end_time_str']
        test_msg = f'Incorrect time-format {start_time_str}-{end_time_str}'

        result = parse_time_from_msg(test_msg, self.local_tz)

        self.assertTupleEqual(result, (None, None))

    def test_only_one_time_entered(self):
        start_time_str = self.time_items['correct']['start_time_str']
        test_msg = f'There only one time entered: {start_time_str}'

        result = parse_time_from_msg(test_msg, self.local_tz)

        self.assertTupleEqual(result, (None, None))

    def test_no_time_in_message(self):
        test_message = 'There is no time in message'

        result = parse_time_from_msg(test_message, self.local_tz)

        self.assertTupleEqual(result, (None, None))


class TestCreateAnswer(unittest.TestCase):

    DATA_STUB = {
        '_id': '',
        'from': {
            'id': '007',
            'name': 'James Bond'
        },
        'conversation': {
            'id': 'MI-6',
            'name': 'Top secret'
        },
        'localTimestamp': '',
        'text': '',
        'entities': [{
            'timezone': '',
        }, ]
    }

    def setUp(self):
        utcnow = datetime.utcnow()
        delta = timedelta(minutes=30)
        self.UTC = pytz.UTC
        self.local_tz = get_localzone()
        self.utc_now = utcnow.astimezone(self.UTC)
        self.start_time = self.utc_now.astimezone(self.local_tz)
        self.end_time = (self.utc_now + delta).astimezone(self.local_tz)
        self.start_time_tmsp = self.start_time.timestamp()
        self.end_time_tmsp = self.end_time.timestamp()
        self.start_time_str = self.start_time.strftime('%H:%M')
        self.end_time_str = self.end_time.strftime('%H:%M')

        self.DATA_STUB['text'] = 'Hello, I am a test message'
        self.DATA_STUB['localTimestamp'] = (self.start_time - delta).isoformat()
        self.DATA_STUB['entities'][0]['timezone'] = self.local_tz.zone

        self.db_instance_mock = mock.MagicMock()
        self.db_instance_mock.get_all_items.return_value = []
        self.db_instance_mock.save.return_value = True

    @mock.patch('tools.message_handlers.parse_time_from_msg')
    @mock.patch('tools.message_handlers.make_response_message')
    def test_time_not_booked_header_accepted(self, make_r_mock, parse_t_mock):
        parse_t_mock.return_value = self.start_time_tmsp, self.end_time_tmsp

        make_r_mock.side_effect = lambda h, all_items: h

        result = create_answer(self.db_instance_mock, self.DATA_STUB)

        self.assertEqual(result, 'Accepted!(cool)')

    @mock.patch('tools.message_handlers.parse_time_from_msg')
    @mock.patch('tools.message_handlers.make_response_message')
    def test_time_already_booked_header_rejected(self, make_mock, parse_mock):
        parse_mock.return_value = self.start_time_tmsp, self.end_time_tmsp

        make_mock.side_effect = lambda h, all_items: h
        self.db_instance_mock.save.return_value = False

        result = create_answer(self.db_instance_mock, self.DATA_STUB)

        self.assertIn('Rejected!', result)

    @mock.patch('tools.message_handlers.parse_time_from_msg')
    def test_time_not_entered_header_is_rejected(self, parse_t_mock):
        parse_t_mock.return_value = (None, None)

        result = create_answer(self.db_instance_mock, self.DATA_STUB)

        self.assertIn('Rejected!', result)


if __name__ == '__main__':
    unittest.main()
