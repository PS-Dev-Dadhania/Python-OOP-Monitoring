from models.base_resource import CloudResource
from utils.logger import get_logger

logger = get_logger(__name__)

class AlertService:
    """
    Service responsible for triggering alerts.
    Demonstrates Separation of Concerns (SoC) - alerting logic is separate from monitoring.
    """
    
    def __init__(self):
        self.active_alerts = []

    def trigger_alert(self, resource: CloudResource, message: str) -> None:
        """Triggers an alert for a specific resource."""
        alert_info = f"ALERT [{resource.resource_id}]: {message}"
        self.active_alerts.append(alert_info)
        logger.warning(alert_info)
        
    def resolve_alert(self, resource_id: str) -> None:
        """Resolves an alert."""
        # Simple resolution logic for demonstration
        self.active_alerts = [a for a in self.active_alerts if resource_id not in a]
        logger.info(f"Alerts resolved for resource ID: {resource_id}")

    def get_active_alerts(self) -> list:
        """Returns the list of active alerts."""
        return self.active_alerts
