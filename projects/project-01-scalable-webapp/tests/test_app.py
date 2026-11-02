import json
import unittest
from unittest.mock import patch

from web.app import database_api_response, route_response


class RouteResponseTests(unittest.TestCase):
    def test_health_returns_200_and_json(self):
        status, body, content_type = route_response("/health")
        self.assertEqual(status, 200)
        self.assertIn("application/json", content_type)
        self.assertEqual(json.loads(body), {"status": "ok"})

    def test_root_returns_html_with_static_asset_and_database_links(self):
        status, body, content_type = route_response("/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", content_type)
        self.assertIn("/static/style.css", body)
        self.assertIn("/database", body)

    def test_static_css_is_served(self):
        status, body, content_type = route_response("/static/style.css")
        self.assertEqual(status, 200)
        self.assertIn("text/css", content_type)
        self.assertIn("font-family", body)

    def test_unknown_route_returns_404(self):
        status, body, content_type = route_response("/missing")
        self.assertEqual(status, 404)
        self.assertIn("application/json", content_type)
        self.assertEqual(json.loads(body), {"error": "not_found"})

    @patch("web.app.database_health")
    def test_database_health_route_returns_database_result(self, mock_health):
        mock_health.return_value = {
            "status": "ok",
            "database": "portfolio",
            "server_time": "2026-11-02T10:00:00+00:00",
        }
        status, body, content_type = database_api_response("/database", "GET")
        self.assertEqual(status, 200)
        self.assertIn("application/json", content_type)
        self.assertEqual(json.loads(body)["database"], "portfolio")

    @patch("web.app.database_health", side_effect=RuntimeError("private connection details"))
    def test_database_health_hides_internal_errors(self, _mock_health):
        status, body, _content_type = database_api_response("/database", "GET")
        self.assertEqual(status, 503)
        self.assertEqual(
            json.loads(body),
            {"status": "error", "message": "Database unavailable"},
        )
        self.assertNotIn("private connection details", body)

    @patch("web.app.create_visit", return_value={"status": "created", "visit_id": 42})
    def test_visits_post_creates_database_record(self, mock_create):
        status, body, content_type = database_api_response("/visits", "POST")
        self.assertEqual(status, 201)
        self.assertIn("application/json", content_type)
        self.assertEqual(json.loads(body)["visit_id"], 42)
        mock_create.assert_called_once_with()

    def test_unhandled_database_route_returns_none(self):
        self.assertIsNone(database_api_response("/unknown", "GET"))


if __name__ == "__main__":
    unittest.main()
