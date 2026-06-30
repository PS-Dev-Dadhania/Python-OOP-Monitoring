import random
from typing import Dict, List
from .base_resource import CloudResource
from utils.logger import get_logger

logger = get_logger(__name__)

class ComputeInstance(CloudResource):
    """
    Represents a Compute Instance resource.
    Demonstrates Inheritance by extending CloudResource.
    """
    
    def __init__(self, resource_id: str, name: str, region: str, instance_type: str, tags: list = []):
        super().__init__(resource_id, name, region, tags)
        self.instance_type = instance_type
        
    def check_health(self) -> bool:
        """
        Checks health specifically for a Compute Instance.
        Demonstrates Polymorphism.
        """
        logger.info(f"Checking health for ComputeInstance {self.name}...")
        # Simulate a health check
        is_healthy = random.choice([True, True, True, False])  # 75% chance of being healthy
        self.status = "HEALTHY" if is_healthy else "OFFLINE"
        return is_healthy

    def collect_metrics(self) -> Dict[str, float]:
        """Collects compute-specific metrics."""
        self._metrics = {
            "cpu_utilization": round(random.uniform(10.0, 95.0), 2),
            "memory_usage": round(random.uniform(20.0, 85.0), 2),
            "network_in": round(random.uniform(100.0, 1000.0), 2),
            "network_out": round(random.uniform(50.0, 500.0), 2)
        }
        return self._metrics
