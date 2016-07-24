"""Tests the REST API application."""

import json
import os
import unittest
import tempfile

from context import api

__author__ = "Travis Knight"
__email__ = "Travisknight@gmail.com"
__license__ = "BSD"

class APITestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, api.app.config['DATABASE'] = tempfile.mkstemp()
        api.app.config['TESTING'] = True
        self.app = api.app.test_client()
        with api.app.app_context():
            api.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(api.app.config['DATABASE'])

    def test_404(self):
        """Tests that non-existent routes return a 404."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 404)

    def test_404_msg(self):
        """Tests 404 response messages."""
        response = self.app.get('/')
        self.assertEqual(data(response)['error'], 'The requested resource was not found.')

    def test_200(self):
        """Tests that the primary route returns a 200."""
        response = self.app.get('/businesses')
        self.assertEqual(response.status_code, 200)

    def test_id_1(self):
        """Tests the first business entry."""
        response = self.app.get('/businesses/1')
        self.assertEqual(data(response)['businesses']['id'], 1)


def data(resp):
    """Returns the JSON data of a response object.

    Args:
        resp (Response): The Response object containing JSON data.

    Returns:
        json: The response data in JSON format.
    """
    return json.loads(resp.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
