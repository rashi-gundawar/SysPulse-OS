import unittest
from fastapi.testclient import TestClient
from backend.api import app
class ApiIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.client=TestClient(app)
    def test_health(self):
        r=self.client.get("/api/health");self.assertEqual(r.status_code,200);self.assertEqual(r.json()["status"],"ok")
    def test_thresholds(self):
        r=self.client.get("/api/settings/thresholds");self.assertEqual(r.status_code,200);self.assertIn("cpu_warning",r.json())
    def test_report_endpoint(self):
        r=self.client.get("/api/report");self.assertEqual(r.status_code,200);self.assertIn("title",r.json())
    def test_report_download(self):
        r=self.client.get("/api/report/download");self.assertEqual(r.status_code,200);self.assertIn("text/html",r.headers["content-type"])
if __name__=="__main__":unittest.main()
