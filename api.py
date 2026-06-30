import asyncio
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from models.compute import ComputeInstance
from models.storage import StorageBucket
from services.alert_service import AlertService
from services.monitor_service import MonitorService
from utils.logger import get_logger

logger = get_logger(__name__)
# Suppress noisy uvicorn access logs
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

app = FastAPI(title="AetherWatch API")

# Initialize Services
alert_service = AlertService()
monitor_service = MonitorService(alert_service)

# Initialize Resources
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

# Apply intentional bug tag
web_server.add_tag("environment:production")

monitor_service.register_resource(web_server)
monitor_service.register_resource(db_server)
monitor_service.register_resource(assets_bucket)

async def simulation_loop():
    logger.info("Starting background simulation loop...")
    while True:
        try:
            monitor_service.run_health_checks()
            monitor_service.collect_all_metrics()
            
            # Clear alerts periodically if they resolve to simulate realistic monitoring
            # In the original, the AlertService just kept growing. Let's just keep it as is
            # but maybe clear old ones or just let the frontend only show active ones.
            # Actually, `run_health_checks` triggers alerts if not healthy, but doesn't resolve them.
            # Let's clear the alert list before each check so we only show CURRENT alerts.
            alert_service._alerts.clear() 
            
        except Exception as e:
            logger.error(f"Error in simulation loop: {e}")
            
        await asyncio.sleep(2)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulation_loop())

@app.get("/api/status")
async def get_status():
    resources_data = []
    for res in monitor_service.resources:
        data = {
            "name": res.name,
            "resource_id": res.resource_id,
            "type": res.__class__.__name__,
            "region": res._region, # Using internal because region isn't exposed via property
            "status": res.status,
            "tags": res.get_tags(),
            "metrics": res._metrics
        }
        resources_data.append(data)
        
    alerts = alert_service.get_active_alerts()
    return {
        "resources": resources_data,
        "alerts": alerts
    }

# Create frontend directory if it doesn't exist to prevent mounting errors
os.makedirs("frontend", exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("frontend/index.html")
