from datetime import datetime


def tmsp_filter(tmsp):
    time = datetime.fromtimestamp(tmsp).time()
    return f'{time.hour}:{time.minute}'
