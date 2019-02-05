import unittest
import mock
import requests
from django.test import Client
from mock import MagicMock, Mock, patch


class HealthcheckEndpointTest(unittest.TestCase):
    def mock_celery_get_stats(self):
        stats = Mock()
        stats.values = MagicMock(return_value=True)
        return stats

    @patch.object(requests, "get")
    @mock.patch("advisers.healthchecks.get_stats")
    def test_healthcheck_returns_ok_if_all_checks_pass(self, get_stats, mockget):
        mockresponse = Mock()
        mockget.return_value = mockresponse
        mockresponse.status_code = 200
        mockresponse.text = """{
            "status": 200,
            "result": [
                {
                    "query": "OX49 5NU",
                    "result": {
                        "postcode": "OX49 5NU",
                        "quality": 1,
                        "eastings": 464447,
                        "northings": 195647,
                        "country": "England",
                        "nhs_ha": "South Central",
                        "longitude": -1.069752,
                        "latitude": 51.655929,
                        "european_electoral_region": "South East",
                        "primary_care_trust": "Oxfordshire",
                        "region": "South East",
                        "lsoa": "South Oxfordshire 011B",
                        "msoa": "South Oxfordshire 011",
                        "incode": "5NU",
                        "outcode": "OX49",
                        "parliamentary_constituency": "Henley",
                        "admin_district": "South Oxfordshire",
                        "parish": "Brightwell Baldwin",
                        "admin_county": "Oxfordshire",
                        "admin_ward": "Chalgrove",
                        "ced": "Chalgrove and Watlington",
                        "ccg": "NHS Oxfordshire",
                        "nuts": "Oxfordshire",
                        "codes": {
                            "admin_district": "E07000179",
                            "admin_county": "E10000025",
                            "admin_ward": "E05009735",
                            "parish": "E04008109",
                            "parliamentary_constituency": "E14000742",
                            "ccg": "E38000136",
                            "ced": "E58001238",
                            "nuts": "UKJ14",
                        },
                    },
                }
            ],
        }"""

        get_stats.side_effect = self.mock_celery_get_stats
        c = Client()
        response = c.get("/healthcheck.json")
        self.assertEquals(200, response.status_code)
