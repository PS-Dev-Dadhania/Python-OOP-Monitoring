import unittest
from unittest.mock import Mock, patch

from models.compute import ComputeInstance
from services.alert_service import AlertService
from services.monitor_service import MonitorService

class TestMonitorService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.alert_service = AlertService()
        self.monitor_service = MonitorService(self.alert_service)
        
        # We explicitly pass tags to avoid the shared mutable default argument bug during tests
        self.compute = ComputeInstance(
            resource_id="test-id", 
            name="test-server", 
            region="us-east-1", 
            instance_type="t2.micro",
            tags=[]
        )
        self.monitor_service.register_resource(self.compute)

    def test_register_resource(self):
        """Test that resources are correctly registered."""
        self.assertEqual(len(self.monitor_service.resources), 1)
        self.assertEqual(self.monitor_service.resources[0].name, "test-server")

    @patch('models.compute.ComputeInstance.check_health')
    def test_run_health_checks_healthy(self, mock_check_health):
        """Test health check when resource is healthy."""
        mock_check_health.return_value = True
        
        self.monitor_service.run_health_checks()
        
        self.assertEqual(len(self.alert_service.get_active_alerts()), 0)

    @patch('models.compute.ComputeInstance.check_health')
    def test_run_health_checks_unhealthy(self, mock_check_health):
        """Test health check when resource is unhealthy triggers an alert."""
        mock_check_health.return_value = False
        
        self.monitor_service.run_health_checks()
        
        alerts = self.alert_service.get_active_alerts()
        self.assertEqual(len(alerts), 1)
        self.assertIn("ALERT [test-id]", alerts[0])

if __name__ == '__main__':
    unittest.main()
