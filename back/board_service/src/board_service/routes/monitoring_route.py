from fastapi import APIRouter, status
from shared_models.enums import HealthStatus
from shared_models.models.server_health import ServerHealth

route = APIRouter(
    prefix="/board_monitoring",
    tags=["board_monitoring"],
    responses={404: {"description": "Not found"}},
)


@route.get("/health", status_code=status.HTTP_200_OK, response_model=ServerHealth)
async def health() -> ServerHealth:
    """
    Get Service Health.

    Performs a heartbeat check to verify that the Board service
    is running and capable of handling traffic.

    :return: A JSON object containing the service name and health status.
    """
    return ServerHealth(
        service_name="Board Service",
        status=HealthStatus.UP,
    )
