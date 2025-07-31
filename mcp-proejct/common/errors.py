"""Enhanced error handling utilities for API MCP server (GitHub-style)."""

from typing import Any, Dict, Optional
import json

class APIError(Exception):
    """Base API error class."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class ValidationError(APIError):
    """Validation error for invalid input data."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)

class NotFoundError(APIError):
    """Error for when a resource is not found."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)

class ConnectionError(APIError):
    """Error for connection issues."""
    
    def __init__(self, message: str = "Connection failed"):
        super().__init__(message, status_code=503)

class AuthenticationError(APIError):
    """Error for authentication issues."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class RateLimitError(APIError):
    """Error for rate limiting."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)

def create_api_error(status_code: int, response_data: Any) -> APIError:
    """Create appropriate API error from status code and response data."""
    if isinstance(response_data, dict):
        message = (
            response_data.get("error") or
            response_data.get("message") or
            response_data.get("detail") or
            "Unknown error"
        )
        details = response_data.get("details") or response_data.get("detail")
    else:
        message = str(response_data)
        details = None

    if status_code == 401:
        return AuthenticationError(message)
    elif status_code == 404:
        return NotFoundError(message)
    elif status_code == 422:
        return ValidationError(message, details)
    elif status_code == 429:
        return RateLimitError(message)
    elif status_code >= 500:
        return APIError(f"Server error: {message}", status_code)
    else:
        return APIError(message, status_code, details)

def format_api_error(error: Exception) -> str:
    """Enhanced error formatting with better structure."""
    if isinstance(error, APIError):
        error_data = {
            "success": False,
            "error": error.message,
            "error_type": type(error).__name__,
            "status_code": error.status_code,
        }
        if error.details:
            error_data["details"] = error.details
    else:
        error_data = {
            "success": False,
            "error": str(error),
            "error_type": type(error).__name__
        }
    
    return json.dumps(error_data, indent=2)