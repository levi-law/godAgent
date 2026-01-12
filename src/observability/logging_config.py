"""
LastAgent Enterprise Logging Configuration

Professional, enterprise-grade structured logging using structlog.
Configures JSON output, log rotation, and correlation ID tracking.
"""
from __future__ import annotations

import logging
import os
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

import structlog
from structlog.types import EventDict, Processor


# =============================================================================
# CONTEXT VARIABLES FOR CORRELATION
# =============================================================================
_trace_id: ContextVar[str | None] = ContextVar("trace_id", default=None)
_span_id: ContextVar[str | None] = ContextVar("span_id", default=None)
_request_method: ContextVar[str | None] = ContextVar("request_method", default=None)
_request_path: ContextVar[str | None] = ContextVar("request_path", default=None)
_agent_name: ContextVar[str | None] = ContextVar("agent_name", default=None)
_phase: ContextVar[str | None] = ContextVar("phase", default=None)


def generate_trace_id() -> str:
    """Generate a unique trace ID for request correlation."""
    return uuid.uuid4().hex[:16]


def generate_span_id() -> str:
    """Generate a unique span ID."""
    return uuid.uuid4().hex[:8]


def set_trace_id(trace_id: str) -> None:
    """Set the current trace ID."""
    _trace_id.set(trace_id)


def get_trace_id() -> str | None:
    """Get the current trace ID."""
    return _trace_id.get()


def set_correlation_context(
    trace_id: str | None = None,
    span_id: str | None = None,
    method: str | None = None,
    path: str | None = None,
    agent: str | None = None,
    phase: str | None = None,
) -> None:
    """Set correlation context for the current request."""
    if trace_id is not None:
        _trace_id.set(trace_id)
    if span_id is not None:
        _span_id.set(span_id)
    if method is not None:
        _request_method.set(method)
    if path is not None:
        _request_path.set(path)
    if agent is not None:
        _agent_name.set(agent)
    if phase is not None:
        _phase.set(phase)


def clear_correlation_context() -> None:
    """Clear all correlation context."""
    _trace_id.set(None)
    _span_id.set(None)
    _request_method.set(None)
    _request_path.set(None)
    _agent_name.set(None)
    _phase.set(None)


# =============================================================================
# CUSTOM PROCESSORS
# =============================================================================
def add_correlation_context(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add correlation context to every log entry."""
    trace_id = _trace_id.get()
    if trace_id:
        event_dict["trace_id"] = trace_id
    
    span_id = _span_id.get()
    if span_id:
        event_dict["span_id"] = span_id
    
    method = _request_method.get()
    if method:
        event_dict["method"] = method
    
    path = _request_path.get()
    if path:
        event_dict["path"] = path
    
    agent = _agent_name.get()
    if agent:
        event_dict["agent"] = agent
    
    phase = _phase.get()
    if phase:
        event_dict["phase"] = phase
    
    return event_dict


def add_timestamp(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add ISO timestamp to log entry."""
    event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
    return event_dict


def add_service_info(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add service information."""
    event_dict["service"] = "lastagent"
    return event_dict


# Sensitive fields to redact
SENSITIVE_FIELDS = {"password", "api_key", "token", "secret", "authorization"}


def redact_sensitive_data(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Redact sensitive data from logs."""
    for key in list(event_dict.keys()):
        if any(s in key.lower() for s in SENSITIVE_FIELDS):
            event_dict[key] = "[REDACTED]"
    return event_dict


def format_duration(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Format duration in milliseconds with suffix."""
    if "duration_ms" in event_dict:
        event_dict["duration"] = f"{event_dict['duration_ms']:.2f}ms"
    return event_dict


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
_configured = False


def configure_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    json_output: bool = True,
    console_output: bool = True,
    file_output: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Configure enterprise-grade structured logging.
    
    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files
        json_output: Whether to output JSON format
        console_output: Whether to log to console
        file_output: Whether to log to file
        max_bytes: Max size of log file before rotation
        backup_count: Number of backup files to keep
    """
    global _configured
    if _configured:
        return
    
    # Ensure log directory exists
    if file_output:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Build processor chain
    shared_processors: list[Processor] = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        add_timestamp,
        add_service_info,
        add_correlation_context,
        redact_sensitive_data,
        format_duration,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Choose renderer based on output format
    if json_output:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    
    # Configure structlog
    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Create formatter
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if file_output:
        log_file = Path(log_dir) / "lastagent.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Also log to JSON file for machine processing
    if file_output and not json_output:
        json_formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.JSONRenderer(),
            ],
        )
        json_file = Path(log_dir) / "lastagent.json.log"
        json_handler = RotatingFileHandler(
            json_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        json_handler.setFormatter(json_formatter)
        root_logger.addHandler(json_handler)
    
    _configured = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    if not _configured:
        configure_logging()
    return structlog.get_logger(name or "lastagent")


# =============================================================================
# CONVENIENCE LOGGING FUNCTIONS
# =============================================================================
def log_request_start(method: str, path: str, client_ip: str = "unknown") -> str:
    """Log request start and return trace_id."""
    trace_id = generate_trace_id()
    set_correlation_context(trace_id=trace_id, method=method, path=path)
    
    logger = get_logger("api")
    logger.info(
        "request_received",
        client_ip=client_ip,
    )
    return trace_id


def log_request_end(status_code: int, duration_ms: float) -> None:
    """Log request completion."""
    logger = get_logger("api")
    logger.info(
        "request_completed",
        status_code=status_code,
        duration_ms=duration_ms,
    )


def log_phase_start(phase: str) -> None:
    """Log phase start."""
    set_correlation_context(phase=phase)
    logger = get_logger("orchestrator")
    logger.info(f"{phase.lower()}_started")


def log_phase_end(phase: str, duration_ms: float, **kwargs: Any) -> None:
    """Log phase completion."""
    logger = get_logger("orchestrator")
    logger.info(
        f"{phase.lower()}_completed",
        duration_ms=duration_ms,
        **kwargs,
    )


def log_agent_selected(agent: str, duration_ms: float, reasoning: str = "") -> None:
    """Log agent selection."""
    set_correlation_context(agent=agent)
    logger = get_logger("council")
    logger.info(
        "agent_selected",
        selected_agent=agent,
        duration_ms=duration_ms,
        reasoning=reasoning[:200] if reasoning else "",
    )


def log_agent_execution_start(agent: str) -> None:
    """Log agent execution start."""
    set_correlation_context(agent=agent, phase="EXECUTION")
    logger = get_logger("executor")
    logger.info("execution_started", executing_agent=agent)


def log_agent_execution_end(agent: str, duration_ms: float, success: bool) -> None:
    """Log agent execution completion."""
    logger = get_logger("executor")
    logger.info(
        "execution_completed",
        executing_agent=agent,
        duration_ms=duration_ms,
        success=success,
    )


def log_error(
    event: str,
    error_type: str,
    error_message: str,
    **context: Any,
) -> None:
    """Log an error with full context."""
    logger = get_logger("error")
    logger.error(
        event,
        error_type=error_type,
        error_message=error_message,
        **context,
    )


def log_delegation(from_agent: str, to_agent: str, task_preview: str) -> None:
    """Log inter-agent delegation."""
    logger = get_logger("mesh")
    logger.info(
        "delegation_requested",
        from_agent=from_agent,
        to_agent=to_agent,
        task_preview=task_preview[:100],
    )
