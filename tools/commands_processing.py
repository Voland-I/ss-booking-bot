# This module defines class witch searches
# commands in the message, makes appropriate processing and
# returns answer text message.


import re

from tools.message_processing import make_message_text


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
    _HELP_MESSAGE = ''' To book time you need to enter \n
        prefer time interval in one of the next formats:\n
        \tHH:MM-HH:MM
        or
        \tHH.MM-HH.MM
        To see the list of booked times type 'list'
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
        self._standard_commands = \
            {'list': (re.compile(r'\blist'), self._list_handler),
             'help': (re.compile(r'\bhelp'), self._help_handler), }

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

        for comm_name, (command_regex, handler) in self._commands.items():
            comm_result = command_regex.search(text_message)
            if comm_result:
                return comm_result[0]
        return ''

    def process_command(self, command, **kwargs):
        '''

        :param command: Name of the command.
        :type command: str
        :param kwargs: Possible named args.
        :type kwargs: dict
        :return: The result of executing appropriate handler.
        '''

        regex_and_command_handler = self._commands.get(command)
        if regex_and_command_handler is not None:
            _, handler = regex_and_command_handler
            return handler(**kwargs)
        return self._help_handler()

    def _help_handler(self, **kwargs):
        '''

        :param kwargs: Possible named args.
        :type kwargs: dict
        :return: Text message with help-information.
        :rtype: str
        '''

        return self._HELP_MESSAGE

    def _list_handler(self, **kwargs):
        '''

        :param kwargs: Possible named args.
        :type: dict
        :return: Formatted text message with all reservations.
        :rtype: str
        '''

        group_id = kwargs['group_id']
        all_items = self._db_instance.get_all_items(group_id)
        header = 'All reservations:' if all_items else 'No reservation'
        response_message = make_message_text(header, all_items)
        return response_message
