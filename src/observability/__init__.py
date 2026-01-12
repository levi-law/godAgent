"""
LastAgent Observability Module

Enterprise-grade end-to-end logging, tracing, and debugging capabilities.
"""
from .logger import (
    get_logger as get_basic_logger,
    configure_logging as configure_basic_logging,
    LogLevel,
)
from .tracer import (
    Tracer,
    Span,
    get_tracer,
    trace_context,
)
from .timeline import (
    ExecutionTimeline,
    TimelineEvent,
    get_timeline,
)
from .error_tracker import (
    ErrorTracker,
    ErrorClassification,
    get_error_tracker,
)
from .logging_config import (
    configure_logging,
    get_logger,
    set_correlation_context,
    clear_correlation_context,
    generate_trace_id,
    log_request_start,
    log_request_end,
    log_phase_start,
    log_phase_end,
    log_agent_selected,
    log_agent_execution_start,
    log_agent_execution_end,
    log_error,
    log_delegation,
)
from .middleware import (
    LoggingMiddleware,
    setup_logging_middleware,
)

__all__ = [
    # Basic Logger
    "get_basic_logger",
    "configure_basic_logging",
    "LogLevel",
    # Enterprise Logger (structlog)
    "configure_logging",
    "get_logger",
    "set_correlation_context",
    "clear_correlation_context",
    "generate_trace_id",
    "log_request_start",
    "log_request_end",
    "log_phase_start",
    "log_phase_end",
    "log_agent_selected",
    "log_agent_execution_start",
    "log_agent_execution_end",
    "log_error",
    "log_delegation",
    # Middleware
    "LoggingMiddleware",
    "setup_logging_middleware",
    # Tracer
    "Tracer",
    "Span",
    "get_tracer",
    "trace_context",
    # Timeline
    "ExecutionTimeline",
    "TimelineEvent",
    "get_timeline",
    # Error Tracker
    "ErrorTracker",
    "ErrorClassification",
    "get_error_tracker",
]
