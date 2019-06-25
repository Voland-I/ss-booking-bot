import sys
import os
import unittest

from dotenv import load_dotenv

sys.path.insert(0, os.getcwd())

env_test_file_path = os.path.join(os.path.dirname(__file__),
                                  'fixtures',
                                  '.env_test')

load_dotenv(os.path.join(env_test_file_path))

from application import app
from tools.system_tools import get_value_from_env


class TestWebhook(unittest.TestCase):

    def setUp(self):
        self._app = app
        self._client = app.test_client()

    def test_get_bot_name(self):
        bot_name = get_value_from_env('BOT_NAME')
        webhook_uri = '/api/messages'

        r = self._client.get(webhook_uri)

        self.assertEqual(r.data.decode('UTF-8'), bot_name)


if __name__ == '__main__':
    unittest.main()
