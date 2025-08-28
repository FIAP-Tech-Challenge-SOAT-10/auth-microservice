"""
Prometheus metrics configuration and custom metrics.
"""

from prometheus_client import Counter, Gauge, Histogram, Info
from prometheus_fastapi_instrumentator import Instrumentator, metrics

# Custom metrics
AUTH_REQUESTS_TOTAL = Counter(
    "auth_requests_total",
    "Total number of authentication requests",
    ["method", "endpoint", "status"],
)

AUTH_RESPONSE_TIME = Histogram(
    "auth_response_time_seconds",
    "Authentication request response time",
    ["method", "endpoint"],
)

ACTIVE_USERS = Gauge("active_users_total", "Number of currently active users")

DATABASE_CONNECTIONS = Gauge(
    "database_connections_active", "Number of active database connections"
)

SERVICE_INFO = Info("service_info", "Information about the authentication service")


def setup_metrics() -> Instrumentator:
    """
    Configure Prometheus metrics instrumentation.

    Returns:
        Configured Instrumentator instance
    """
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health", "/health/live", "/health/ready"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )

    # Add default metrics
    instrumentator.add(
        metrics.request_size(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    )

    instrumentator.add(
        metrics.response_size(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    )

    instrumentator.add(
        metrics.latency(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    )

    instrumentator.add(
        metrics.requests(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    )

    # Set service information
    SERVICE_INFO.info(
        {
            "version": "1.0.0",
            "service": "authentication-microservice",
            "environment": "development",  # This should come from config
        }
    )

    return instrumentator


def record_active_users(count: int) -> None:
    """Record the number of active users."""
    ACTIVE_USERS.set(count)


def record_database_connections(count: int) -> None:
    """Record the number of active database connections."""
    DATABASE_CONNECTIONS.set(count)
