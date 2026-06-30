import time
from models.compute import ComputeInstance
from models.storage import StorageBucket
from services.alert_service import AlertService
from services.monitor_service import MonitorService
from utils.logger import get_logger

logger = get_logger(__name__)

def main():
    logger.info("Starting Cloud Resource Monitor...")
    
    # Initialize Services
    alert_service = AlertService()
    monitor_service = MonitorService(alert_service)
    
    # Initialize Resources
    # NOTE: We do not pass 'tags' here to trigger the intentional mutable default argument bug
    # defined in base_resource.py
    web_server = ComputeInstance(
        resource_id="i-0123456789abcdef0",
        name="web-server-01",
        region="us-east-1",
        instance_type="t3.medium"
    )
    
    db_server = ComputeInstance(
        resource_id="i-0abcdef1234567890",
        name="database-server-01",
        region="us-east-1",
        instance_type="m5.large"
    )
    
    assets_bucket = StorageBucket(
        resource_id="b-9876543210fedcba",
        name="company-assets-bucket",
        region="us-west-2",
        capacity_gb=5000
    )
    
    # The intentional bug: Adding a tag to web_server accidentally adds it to db_server and assets_bucket
    # because they share the same list reference from the mutable default argument.
    logger.info("Adding 'environment:production' tag to web_server only...")
    web_server.add_tag("environment:production")
    
    logger.info(f"Tags for web_server: {web_server.get_tags()}")
    logger.info(f"Tags for db_server (Unexpectedly has the tag!): {db_server.get_tags()}")
    logger.info(f"Tags for assets_bucket (Unexpectedly has the tag!): {assets_bucket.get_tags()}")
    
    # Register Resources
    monitor_service.register_resource(web_server)
    monitor_service.register_resource(db_server)
    monitor_service.register_resource(assets_bucket)
    
    # Simulate a monitoring cycle
    for i in range(1, 3):
        logger.info(f"--- Monitoring Cycle {i} ---")
        monitor_service.run_health_checks()
        monitor_service.collect_all_metrics()
        
        alerts = alert_service.get_active_alerts()
        if alerts:
            logger.warning(f"Active Alerts: {len(alerts)}")
            for alert in alerts:
                logger.warning(alert)
        else:
            logger.info("System is fully healthy.")
            
        time.sleep(1)
        
    logger.info("Cloud Resource Monitor shut down.")

if __name__ == "__main__":
    main()
