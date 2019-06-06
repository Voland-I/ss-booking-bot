from datetime import datetime

from tools import parse_time_from_msg


def test_parse_time_from_msg_1130_1200():
    time_start_str, time_end_str = '11:30', '12:00'
    msg_text = f'{time_start_str}-{time_end_str}'
    today = datetime.today().date()
    start_tmsp_control = datetime.combine(
        today, datetime.strptime(time_start_str, '%H:%M').time()).timestamp()

    end_tmsp_control = datetime.combine(
        today, datetime.strptime(time_end_str, '%H:%M').time()).timestamp()

    start_tmsp, end_tmsp = parse_time_from_msg(msg_text)

    assert all((start_tmsp, end_tmsp))
    assert (start_tmsp == start_tmsp_control) and (end_tmsp == end_tmsp_control)


def test_parse_time_from_msg_1130_1200_with_whitespaces():
    time_start_str, time_end_str = '11:30', '12:00'
    msg_text = f'{time_start_str}  -{time_end_str}'
    today = datetime.today().date()
    start_tmsp_control = datetime.combine(
        today, datetime.strptime(time_start_str, '%H:%M').time()).timestamp()

    end_tmsp_control = datetime.combine(
        today, datetime.strptime(time_end_str, '%H:%M').time()).timestamp()

    start_tmsp, end_tmsp = parse_time_from_msg(msg_text)

    assert all((start_tmsp, end_tmsp))
    assert (start_tmsp == start_tmsp_control) and (end_tmsp == end_tmsp_control)


def test_parse_time_from_msg_1130_1200_with_some_text():
    time_start_str, time_end_str = '11:30', '12:00'
    msg_text = f'some text before, {time_start_str}-{time_end_str} and after'
    today = datetime.today().date()
    start_tmsp_control = datetime.combine(
        today, datetime.strptime(time_start_str, '%H:%M').time()).timestamp()

    end_tmsp_control = datetime.combine(
        today, datetime.strptime(time_end_str, '%H:%M').time()).timestamp()

    start_tmsp, end_tmsp = parse_time_from_msg(msg_text)

    assert all((start_tmsp, end_tmsp))
    assert (start_tmsp == start_tmsp_control) and (end_tmsp == end_tmsp_control)


def test_parse_time_from_msg_start_equal_end_time():
    time_start_str, time_end_str = '11:30', '11:30'
    msg_text = f'some text before, {time_start_str}-{time_end_str} and after'

    start_tmsp, end_tmsp = parse_time_from_msg(msg_text)

    assert not any((start_tmsp, end_tmsp))


def test_parse_time_from_msg_1200_1130():
    time_start_str, time_end_str = '12:00', '11:30'
    msg_text = f'{time_start_str}-{time_end_str}'

    start_tmsp, end_tmsp = parse_time_from_msg(msg_text)

    assert not any((start_tmsp, end_tmsp))
