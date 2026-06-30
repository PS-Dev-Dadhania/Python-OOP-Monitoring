from typing import List
from models.base_resource import CloudResource
from services.alert_service import AlertService
from exceptions.errors import HealthCheckError
from utils.logger import get_logger

logger = get_logger(__name__)

class MonitorService:
    """
    Service responsible for orchestrating resource monitoring.
    Demonstrates Dependency Injection by accepting an AlertService.
    """
    
    def __init__(self, alert_service: AlertService):
        self.resources: List[CloudResource] = []
        self.alert_service = alert_service

    def register_resource(self, resource: CloudResource) -> None:
        """Registers a new cloud resource for monitoring."""
        self.resources.append(resource)
        logger.info(f"Registered resource: {resource.name} ({resource.resource_id})")

    def run_health_checks(self) -> None:
        """
        Iterates through all registered resources and performs health checks.
        Demonstrates Polymorphism as check_health() behaves differently depending
        on the underlying object type (ComputeInstance vs StorageBucket).
        """
        logger.info("Starting system-wide health checks...")
        
        for resource in self.resources:
            try:
                is_healthy = resource.check_health()
                
                if not is_healthy:
                    self.alert_service.trigger_alert(
                        resource, 
                        f"Health check failed. Status is {resource.status}"
                    )
            except Exception as e:
                # Catch unexpected errors and raise a domain-specific exception
                logger.error(f"Failed to check health for {resource.name}: {str(e)}")
                raise HealthCheckError(f"Critical failure during health check for {resource.name}") from e

    def collect_all_metrics(self) -> dict:
        """
        Collects metrics from all registered resources.
        Demonstrates Polymorphism.
        """
        logger.info("Collecting metrics from all resources...")
        report = {}
        
        for resource in self.resources:
            metrics = resource.collect_metrics()
            report[resource.name] = metrics
            logger.info(f"Metrics for {resource.name}: {metrics}")
            
        return report
