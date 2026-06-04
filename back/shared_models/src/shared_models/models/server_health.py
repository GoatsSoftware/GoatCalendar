from pydantic import BaseModel

from shared_models.enums import HealthStatus


class ServerHealth(BaseModel):
    """
    Schema representing the health status of the application.

    :param service_name: The descriptive name of the identity service.
    :param status: The current operational status of the service.
    """

    service_name: str
    status: HealthStatus
