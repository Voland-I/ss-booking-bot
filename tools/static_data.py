HEADERS = {
    'incorrect_enter': 'Incorrect time or command:|',
    'time_booked': 'Rejected! Time already booked!',
    'accepted': 'Accepted!'
}

MESSAGES = {
    'help': '''
    To book a time-slot you need to enter prefer time interval in one 
    of the next formats: 
    \tHH:MM-HH:MM
    or 
    \tHH.MM-HH.MM
    To see the list of already booked time-slots type 'list';
    To cancel one of the booked time-slots type 'cancel <number of time-slot>
    ''',

    'welcome': '''
Hi all!\n
To see all available commands type help!
'''
}

CANCEL_COMMAND_HEADERS = {
    'not_exists': 'No such item',
    'not_owner': 'Rejected to delete item, you aren\'t owner',
    'deleted': 'Deleted slot for',
    'any_number': 'Please, select a number of time-slot',
    'in_past': 'This game already ended!'
}

LIST_COMMAND_HEADERS = {
    'empty': 'Any reservations!\n',
    'not_empty': 'All reservations:\n'
}

GAME_STATUSES = {
    'played': '(y)',
    'in_process': '(punch)',
    'will_be': '(fistbump)'
}


help_message_backup = (
             '<p style="font-size: 12px;"> To book time you need to enter '
             'prefer time interval in one of the next formats:</p>'
             '\t<b>HH:MM-HH:MM</b>'
             'or'
             '\t<b>HH.MM-HH.MM</b>'
             '<p style="font-size: 12px">To see the '
             'list of booked times type *asterisks*\'list\'*asterisks*'
             'To cancel one of your booked time-slot'
             'type *asterisks*\'cancel <number of slot>\'*asterisks*</p>'
)
