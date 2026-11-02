import json
import unittest

from application.web.app import route_response


class RouteResponseTests(unittest.TestCase):
    def test_health_returns_200_and_json(self):
        status, body, content_type = route_response("/health")
        self.assertEqual(status, 200)
        self.assertIn("application/json", content_type)
        self.assertEqual(json.loads(body), {"status": "ok"})

    def test_root_returns_html(self):
        status, body, content_type = route_response("/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", content_type)
        self.assertIn("AWS Scalable Web Application", body)

    def test_unknown_route_returns_404(self):
        status, body, content_type = route_response("/missing")
        self.assertEqual(status, 404)
        self.assertIn("application/json", content_type)
        self.assertEqual(json.loads(body), {"error": "not_found"})


if __name__ == "__main__":
    unittest.main()
