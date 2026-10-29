import unittest
from backend.collectors.system_metrics import collect_system_metrics
from backend.collectors.disk_metrics import collect_disk_metrics
from backend.collectors.process_metrics import collect_process_metrics
class CollectorTests(unittest.TestCase):
    def test_system_shape(self):
        m=collect_system_metrics();self.assertIn("timestamp",m);self.assertIn("uptime_seconds",m);self.assertGreaterEqual(m["cpu_percent"],0)
    def test_disk_range(self):
        d=collect_disk_metrics("/");self.assertGreater(d["total"],0);self.assertLessEqual(d["percent"],100)
    def test_process_limit(self):self.assertLessEqual(len(collect_process_metrics(3)),3)
    def test_process_shape(self):
        p=collect_process_metrics(2);self.assertTrue(p);self.assertIn("pid",p[0])
if __name__=="__main__":unittest.main()
