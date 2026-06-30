from abc import ABC, abstractmethod
from typing import List, Dict

class CloudResource(ABC):
    """
    Abstract Base Class for all cloud resources.
    Demonstrates Abstraction by defining a common contract for resources.
    """
    
    # INTENTIONAL BUG: Mutable default argument 'tags'
    # In Python, default arguments are evaluated once when the function is defined.
    # Therefore, all instances created without passing 'tags' will share the same list object.
    def __init__(self, resource_id: str, name: str, region: str, tags: list = []):
        self._resource_id = resource_id
        self._name = name
        self._region = region
        self._tags = tags  # This is the shared list if no tags are provided
        self._status = "UNKNOWN"
        self._metrics: Dict[str, float] = {}

    @property
    def resource_id(self) -> str:
        """Encapsulates the resource ID (Read-only property)."""
        return self._resource_id

    @property
    def name(self) -> str:
        """Encapsulates the resource name."""
        return self._name

    @property
    def status(self) -> str:
        """Encapsulates the resource status."""
        return self._status

    @status.setter
    def status(self, new_status: str) -> None:
        """Setter with basic validation."""
        valid_statuses = ["HEALTHY", "DEGRADED", "OFFLINE", "UNKNOWN"]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")
        self._status = new_status

    def add_tag(self, tag: str) -> None:
        """Adds a tag to the resource."""
        self._tags.append(tag)
        
    def get_tags(self) -> List[str]:
        """Returns the list of tags."""
        return self._tags

    @abstractmethod
    def check_health(self) -> bool:
        """
        Abstract method to check the health of the resource.
        Must be implemented by all subclasses (Polymorphism).
        """
        pass

    @abstractmethod
    def collect_metrics(self) -> Dict[str, float]:
        """
        Abstract method to collect metrics.
        Must be implemented by all subclasses.
        """
        pass
