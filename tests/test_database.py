import unittest
from backend.diagnostics.diagnostic_engine import diagnose
from database.database_manager import initialize_database,get_metrics,get_alerts
class DatabaseTests(unittest.TestCase):
    def test_init_and_read(self):
        initialize_database();self.assertIsInstance(get_metrics(3),list);self.assertIsInstance(get_alerts(3),list)
if __name__=="__main__":unittest.main()
