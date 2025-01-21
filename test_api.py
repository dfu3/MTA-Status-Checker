import unittest
from datetime import datetime, timedelta
from flask import Flask
from update_data import DELAYS
from api import calculate_uptime, app

class TestAPI(unittest.TestCase):
    def setUp(self):
        """
        Set up test data and a Flask test client.
        """
        self.test_client = app.test_client()
        self.service_start = datetime.now() - timedelta(hours=10)  # Service started 10 hours ago
        DELAYS.clear()  # Clear any existing delays in the global variable

    def test_calculate_uptime_no_delays(self):
        """
        Test calculate_uptime when there are no delays.
        """
        line_data = {
            'total_delayed': 0,
            'currently_delayed': False
        }
        service_time = 36000  # 10 hours in seconds
        uptime = calculate_uptime(line_data, service_time)
        self.assertAlmostEqual(uptime, 1.0)

    def test_calculate_uptime_with_delays(self):
        """
        Test calculate_uptime when the line has been delayed.
        """
        delay_start = datetime.now() - timedelta(minutes=30)
        line_data = {
            'total_delayed': 1200,  # 20 minutes in seconds
            'currently_delayed': True,
            'delay_start': delay_start
        }
        service_time = 36000  # 10 hours in seconds
        uptime = calculate_uptime(line_data, service_time)
        expected_uptime = 1 - ((1200 + (datetime.now() - delay_start).total_seconds()) / service_time)
        self.assertAlmostEqual(uptime, expected_uptime, places=5)

    def test_uptime_route_no_delays(self):
        """
        Test the /uptime/<line> route when the line has no delays.
        """
        line = 'A'
        DELAYS[line] = {
            'total_delayed': 0,
            'currently_delayed': False,
            'delay_start': None
        }
        response = self.test_client.get(f'/uptime/{line}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['Line'], line)
        self.assertAlmostEqual(data['Uptime'], 1.0)

    def test_status_route_delayed(self):
        """
        Test the /status/<line> route when the line is delayed.
        """
        line = 'A'
        DELAYS[line] = {
            'total_delayed': 0,
            'currently_delayed': True,
            'delay_start': datetime.now() - timedelta(minutes=15)
        }
        response = self.test_client.get(f'/status/{line}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['Line'], line)
        self.assertTrue(data['Delayed'])

    def test_status_route_not_delayed(self):
        """
        Test the /status/<line> route when the line is not delayed.
        """
        line = 'A'
        DELAYS[line] = {
            'total_delayed': 0,
            'currently_delayed': False,
            'delay_start': None
        }
        response = self.test_client.get(f'/status/{line}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['Line'], line)
        self.assertFalse(data['Delayed'])

    def test_status_route_line_not_found(self):
        """
        Test the /status/<line> route when the line is not found in DELAYS.
        """
        line = 'Z'
        response = self.test_client.get(f'/status/{line}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['Line'], line)
        self.assertFalse(data['Delayed'])

if __name__ == '__main__':
    unittest.main()
