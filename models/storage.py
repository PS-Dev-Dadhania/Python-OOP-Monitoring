import random
from typing import Dict, List
from .base_resource import CloudResource
from utils.logger import get_logger

logger = get_logger(__name__)

class StorageBucket(CloudResource):
    """
    Represents a Cloud Storage Bucket.
    Demonstrates Inheritance by extending CloudResource.
    """
    
    def __init__(self, resource_id: str, name: str, region: str, capacity_gb: int, tags: list = []):
        super().__init__(resource_id, name, region, tags)
        self.capacity_gb = capacity_gb
        
    def check_health(self) -> bool:
        """
        Checks health specifically for a Storage Bucket.
        Demonstrates Polymorphism.
        """
        logger.info(f"Checking health for StorageBucket {self.name}...")
        # Simulate a health check (storage is usually more reliable)
        is_healthy = random.choice([True, True, True, True, False])  # 80% chance of being healthy
        self.status = "HEALTHY" if is_healthy else "DEGRADED"
        return is_healthy

    def collect_metrics(self) -> Dict[str, float]:
        """Collects storage-specific metrics."""
        used_capacity = round(random.uniform(0.0, self.capacity_gb), 2)
        self._metrics = {
            "used_capacity_gb": used_capacity,
            "free_capacity_gb": round(self.capacity_gb - used_capacity, 2),
            "read_operations": round(random.uniform(1000.0, 50000.0), 2),
            "write_operations": round(random.uniform(100.0, 10000.0), 2)
        }
        return self._metrics
