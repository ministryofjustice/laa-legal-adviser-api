import unittest
import mock
from django.test import Client
from mock import MagicMock, Mock

class HealthcheckEndpointTest(unittest.TestCase):
	def mock_celery_get_stats(self):
		stats = Mock()
		stats.values = MagicMock(return_value=True)
		return stats

	@mock.patch('advisers.healthchecks.get_stats')
	def test_healthcheck_returns_ok_if_all_checks_pass(self, get_stats):
		get_stats.side_effect = self.mock_celery_get_stats
		c = Client()
		response = c.get("/healthcheck.json")
		self.assertEquals(200, response.status_code)