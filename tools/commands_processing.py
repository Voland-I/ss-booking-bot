# This module defines class witch searches
# commands in the message, makes appropriate processing and
# returns answer text message.


import re
from datetime import datetime
import pytz

from tools.message_processing import make_message_text
from tools.static_data import CANCEL_COMMAND_HEADERS, MESSAGES, LIST_COMMAND_HEADERS
from tools.time_tools import get_tzname_from_request


class CommandsProcessor:
    # CommandsProcessor designed for commands processing
    # from the message.  It's defines two methods (parse_command and
    # process command) for commands parsing from the text message and
    # execute them.  It also contains collection with standard
    # commands ('help' and 'list'), them handlers (_help_handler and
    # _list_handler) and _HELP_MESSAGE data attribute
    # with help-message.

    # This attribute contains help-message as response to
    # 'help' command.
    _HELP_MESSAGE = '''
        <p style="font-size: 12px;"> To book time you need to enter \n
        prefer time interval in one of the next formats:</p>\n
        \t<b>HH:MM-HH:MM</b>
        or
        \t<b>HH.MM-HH.MM</b>\n
        <p style="font-size: 12px">To see the \n
        list of booked times type <b>'list'</b>\n
        To cancel one of your booked time-slot\n
        type <b>'cancel <number of slot>'</b></p>
    '''

    def __init__(self, db_instance, commands=None):
        '''

        :param db_instance: Instance of database client.
        :type db_instance: tools.db_client.DatabaseClient
        :param commands: Collection witch contains regexes
                        for commands parsing and handlers for them.
        :type commands: dict
        '''

        self._db_instance = db_instance

        # This attribute contains collection with commands witch
        # CommandProcessor class supports.  But user can imitate this
        self._standard_commands = {
            'list': (
                (
                    lambda row: re.findall(r'\blist\b', row),
                    lambda row: ['list', ] if not row else ''
                ),
                self._list_handler
            ),

            'help': (
                (
                    lambda row: re.findall(r'\bhelp\b', row),
                ),
                self._help_handler
            ),
            'cancel': (
                (
                    lambda row: re.findall(r'\bcancel\s*\d{1,1}', row),
                ),
                self._cancel_handler
            )
        }

        # user can defines himself commands and command-handlers
        # by passing 'commands' parameter or use standard
        # commands 'help' and 'list'
        self._commands = commands or self._standard_commands

    def parse_command(self, text_message):
        '''

        :param text_message: User's text message.
        :type text_message: str
        :return Command name or None.
        :rtype: str
        '''

        for comm_name, (command_parsers, handler) in self._commands.items():
            for command_parser in command_parsers:
                matches = command_parser(text_message)
                if matches:
                    return comm_name, matches[0]
        return None, None

    def process_command(self, command_name, command_entity, **kwargs):
        '''

        :param command_name: Name of the command.
        :type command_name: str
        :param command_entity: parsed text with command name and parameters.
        :type command_entity: str
        :param kwargs: Possible named args.
        :type kwargs: dict
        :return: The result of executing appropriate handler.
        '''

        regex_and_command_handler = self._commands.get(command_name)
        if regex_and_command_handler is not None:
            _, handler = regex_and_command_handler
            result = handler(command_entity, **kwargs)
            return result
        return self._help_handler(command_entity, **kwargs)

    def _help_handler(self, command_entity, **kwargs):
        '''

        :param command_entity: parsed text with command and parameters.
        :type command_entity: str
        :param kwargs: Possible named args.
        :type kwargs: dict
        :return: Text message with help-information.
        :rtype: str
        '''

        return MESSAGES['help']

    def _list_handler(self, command_entity, **kwargs):
        '''

        :param command_entity: parsed text with command and parameters.
        :param kwargs: Possible named args.
        :type: dict
        :return: Formatted text message with all reservations.
        :rtype: str
        '''

        request_data = kwargs['request_data']
        group_id = request_data['conversation']['id']
        all_items = self._db_instance.get_all_items(group_id)
        header = LIST_COMMAND_HEADERS['not_empty'] if all_items else LIST_COMMAND_HEADERS['empty']
        response_message = make_message_text(header, all_items)
        return response_message

    def _cancel_handler(self, command_entity, **kwargs):
        '''

        :param command_entity: parsed text with command and parameters.
        :type command_entity: str
        :param kwargs: Possible named args.
        :type kwargs: dict
        :return: Formatted text message with all reservations.
        '''
        request_data = kwargs['request_data']
        group_id = request_data['conversation']['id']
        user_id = request_data['from']['id']
        tzname = get_tzname_from_request(request_data)
        tz = pytz.timezone(tzname)
        index_to_delete = re.search(r'\d{1,1}', command_entity)
        local_now = datetime.now(tz=tz).time()
        local_now_delta = 60*local_now.hour + local_now.minute
        if index_to_delete:
            index_to_delete = int(index_to_delete.group(0)) - 1
        all_items = self._db_instance.get_all_items(group_id)
        response_message = CANCEL_COMMAND_HEADERS['not_exist']
        if index_to_delete < len(all_items):
            item_to_delete = all_items[index_to_delete]
            response_message = CANCEL_COMMAND_HEADERS['rejected']
            if item_to_delete['user_id'] == user_id:
                response_message = CANCEL_COMMAND_HEADERS['game_in_past']
                if item_to_delete['end_delta'] <= local_now_delta:
                    item_id = item_to_delete['_id']
                    self._db_instance.delete_item(group_id, item_id)
                    response_message = (f'{CANCEL_COMMAND_HEADERS["deleted"]} '
                                    f'{item_to_delete["start_time_str"]}-'
                                    f'{item_to_delete["end_time_str"]}'
                                    f'for user {item_to_delete["user_name"]}')

        return response_message

