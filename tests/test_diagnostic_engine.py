import unittest
from backend.diagnostics.diagnostic_engine import diagnose,validate_thresholds
class DiagnosticTests(unittest.TestCase):
    def sample(self,cpu=10,mem=20,disk=30):return {"timestamp":"test","cpu_percent":cpu,"memory":{"percent":mem},"disk":{"percent":disk},"network":{"counts":{"established":0,"listening":0}}}
    def test_healthy(self):self.assertEqual(diagnose(self.sample())["overall_health"],"HEALTHY")
    def test_cpu_critical(self):self.assertEqual(diagnose(self.sample(cpu=95))["overall_health"],"CRITICAL")
    def test_memory_warning(self):self.assertTrue(any(a["category"]=="Memory" for a in diagnose(self.sample(mem=80))["alerts"]))
    def test_disk_warning(self):self.assertTrue(any(a["category"]=="Disk" for a in diagnose(self.sample(disk=85))["alerts"]))
    def test_sustained(self):
        hist=[{"cpu_percent":75,"memory_percent":10,"disk_percent":10} for _ in range(3)]
        self.assertTrue(any(a["rule"]=="sustained_threshold" for a in diagnose(self.sample(cpu=75),{"sustained_samples":3},hist)["alerts"]))
    def test_cpu_diagnostic_includes_top_process(self):
        processes=[{"pid":42,"name":"worker","cpu_percent":88,"memory_percent":1}]
        result=diagnose(self.sample(cpu=80),processes=processes)
        alert=next(a for a in result["alerts"] if a["category"]=="CPU")
        self.assertIn("worker",alert["likely_cause"])
        self.assertIn("Sort processes by CPU",alert["recommended_action"])

    def test_sustained_diagnostic_includes_average_and_recommendation(self):
        hist=[{"cpu_percent":72,"memory_percent":10,"disk_percent":10},
              {"cpu_percent":78,"memory_percent":10,"disk_percent":10},
              {"cpu_percent":75,"memory_percent":10,"disk_percent":10}]
        result=diagnose(self.sample(cpu=75),{"sustained_samples":3},hist)
        alert=next(a for a in result["alerts"] if a["rule"]=="sustained_threshold")
        self.assertIn("average",alert["message"])
        self.assertTrue(alert["recommended_action"])

    def test_threshold_validation(self):
        with self.assertRaises(ValueError):validate_thresholds({"cpu_warning":95,"cpu_critical":90})
    def test_network_heuristic(self):
        m=self.sample();m["network"]["counts"]["established"]=200
        self.assertTrue(any(a["category"]=="Network" for a in diagnose(m)["alerts"]))
if __name__=="__main__":unittest.main()
