import os

from tools.system_tools import get_value_from_env


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    BASE_DIR = BASE_DIR

    DEBUG = False

    SECRET_KEY = get_value_from_env('SECRET_KEY')
    APP_ID = get_value_from_env('APP_ID')
    APP_PASS = get_value_from_env('APP_PASSWORD')

    SERVICE_URI = get_value_from_env('SERVICE_URI')

    DB_URI = get_value_from_env('MONGODB_URI')
    DB_NAME = get_value_from_env('MONGODB_NAME')
