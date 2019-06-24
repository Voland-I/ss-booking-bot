import re

from tools.message_processing import make_message_text


class CommandsProcessor:
    _HELP_MESSAGE = ''' 
        To book time you need to enter \n
        prefer time interval in formats:\n
        \thh:mm-hh:mm
        or
        \thh.mm-hh.mm
        To see the list of booked times type 'list'
    '''

    _STANDART_COMMANDS = {'list': re.compile(r'\blist'),
                          'help': re.compile(r'\bhelp'), }

    def __init__(self, db_instance, commands=None):
        self._db_instance = db_instance
        self._commands = commands or self._STANDART_COMMANDS

    def parse_command(self, text_message):
        for comm_name, command_regex in self._commands.items():
            comm_result = command_regex.search(text_message)
            if comm_result:
                return comm_result[0]
        return None

    def process_command(self, command, group_id):
        response_message = ''
        if command == 'list':
            all_items = self._db_instance.get_all_items(group_id)
            header = 'All reservations:' if all_items else 'No reservations'
            response_message = make_message_text(header, all_items)
        if command == 'help':
            response_message = self._HELP_MESSAGE

        return response_message
