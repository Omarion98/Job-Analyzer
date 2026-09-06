import logging
import os

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace


logger = logging.getLogger("uvicorn.error")


def setup_telemetry() -> None:
    """
    Configure Azure Monitor / Application Insights when a connection
    string is available. Local development still works without it.
    """
    connection_string = os.getenv(
        "APPLICATIONINSIGHTS_CONNECTION_STRING"
    )

    if not connection_string:
        logger.info(
            "Application Insights disabled: "
            "APPLICATIONINSIGHTS_CONNECTION_STRING is not set."
        )
        return

    configure_azure_monitor(
        connection_string=connection_string,
    )

    logger.info("Application Insights enabled.")


def get_tracer(component: str):
    """
    Return an OpenTelemetry tracer for a project component.
    """
    return trace.get_tracer(
        f"career-copilot.{component}"
    )
