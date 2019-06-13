from os.path import abspath, dirname

from tools.system_tools import get_value_from_env


class Config:
    BASE_DIR = abspath(dirname(__file__))

    DEBUG = False

    BOT_NAME = get_value_from_env('BOT_NAME')

    SECRET_KEY = get_value_from_env('SECRET_KEY')
    APP_ID = get_value_from_env('APP_ID')
    APP_PASS = get_value_from_env('APP_PASSWORD')

    DB_URI = get_value_from_env('MONGODB_URI')
    DB_NAME = get_value_from_env('MONGODB_NAME')
