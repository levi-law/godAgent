"""
LastAgent Logging Middleware

FastAPI middleware for automatic request/response logging with correlation IDs.
"""
from __future__ import annotations

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .logging_config import (
    configure_logging,
    get_logger,
    generate_trace_id,
    set_correlation_context,
    clear_correlation_context,
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs all HTTP requests and responses.
    
    Features:
    - Generates unique trace_id for each request
    - Logs request entry with method, path, client IP
    - Logs response exit with status code and duration
    - Automatically clears correlation context after request
    """
    
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        # Generate trace ID
        trace_id = generate_trace_id()
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Set correlation context
        set_correlation_context(
            trace_id=trace_id,
            method=request.method,
            path=request.url.path,
        )
        
        # Add trace_id to request state for downstream access
        request.state.trace_id = trace_id
        
        # Log request
        logger = get_logger("api.middleware")
        logger.info(
            "request_started",
            client_ip=client_ip,
            query_params=str(request.query_params) if request.query_params else None,
            user_agent=request.headers.get("user-agent", "unknown")[:100],
        )
        
        # Track timing
        start_time = time.perf_counter()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Log successful response
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )
            
            # Add trace_id to response headers for debugging
            response.headers["X-Trace-ID"] = trace_id
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Log error
            logger.error(
                "request_failed",
                error_type=type(e).__name__,
                error_message=str(e)[:500],
                duration_ms=round(duration_ms, 2),
            )
            raise
            
        finally:
            # Clean up correlation context
            clear_correlation_context()


def setup_logging_middleware(app) -> None:
    """
    Configure logging and add middleware to FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    # Configure structlog
    configure_logging(
        log_level="INFO",
        log_dir="logs",
        json_output=True,
        console_output=True,
        file_output=True,
    )
    
    # Add middleware
    app.add_middleware(LoggingMiddleware)
    
    # Log startup
    logger = get_logger("app")
    logger.info("application_initialized", version="0.1.0")
