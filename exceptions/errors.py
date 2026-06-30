class CloudMonitorError(Exception):
    """Base exception for all Cloud Monitor errors."""
    pass

class ResourceNotFoundError(CloudMonitorError):
    """Raised when a specified resource cannot be found."""
    pass

class HealthCheckError(CloudMonitorError):
    """Raised when a resource health check fails unexpectedly."""
    pass

class ConfigurationError(CloudMonitorError):
    """Raised when there is a configuration error."""
    pass
