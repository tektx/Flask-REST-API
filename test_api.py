"""Tests the REST API application.
"""

import json
import unittest
import api

__author__ = "Travis Knight"
__email__ = "Travisknight@gmail.com"
__license__ = "BSD"

class APITestCase(unittest.TestCase):

    def setUp(self):
        self.db = api.create_db('sample.csv')
        self.app = api.app.test_client()

    def tearDown(self):
        pass

    def test_404(self):
        """Checks that 404 errors include their status code in the response.
        """
        response = json.loads(self.app.get('/').data)
        self.assertEqual(response['status'], 404)

    def test_pagination(self):
        response = json.loads(self.app.get('/businesses').data)
        print response


if __name__ == '__main__':
    unittest.main()
