"""Enhanced utilities for API MCP server (GitHub-style)."""

import httpx
import json
from typing import Any, Dict, Optional, Union
from .types import APIResponse, ErrorResponse
from .errors import APIError, ValidationError, NotFoundError
import logging

# Setup logging
logger = logging.getLogger(__name__)

# API Configuration
API_BASE_URL = "http://127.0.0.1:8001"
DEFAULT_TIMEOUT = 30.0
USER_AGENT = "api-mcp-client/1.0.0"

class APIClient:
    """Enhanced API client with better error handling and utils."""
    
    def __init__(self, base_url: str = API_BASE_URL, timeout: float = DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.headers = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """Enhanced HTTP request with better error handling."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Clean up params - remove None values
        if params:
            params = {k: v for k, v in params.items() if v is not None}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    json=json_data,
                    params=params,
                    headers=self.headers,
                    timeout=self.timeout,
                    **kwargs
                )
                
                return await self._handle_response(response)
                
            except httpx.TimeoutException:
                raise APIError("Request timeout", status_code=408)
            except httpx.ConnectError:
                raise APIError("Connection failed - is the API server running?", status_code=503)
            except Exception as e:
                logger.error(f"Unexpected error in API request: {e}")
                raise APIError(f"Request failed: {e}")

    async def _handle_response(self, response: httpx.Response) -> Any:
        """Handle HTTP response and convert to appropriate exceptions."""
        try:
            response_data = response.json()
        except Exception:
            response_data = {"message": response.text}

        if response.is_success:
            return response_data
        
        # Handle different error status codes
        error_message = self._extract_error_message(response_data)
        
        if response.status_code == 404:
            raise NotFoundError(error_message)
        elif response.status_code == 422:
            raise ValidationError(error_message, details=response_data.get("detail"))
        elif 400 <= response.status_code < 500:
            raise APIError(error_message, status_code=response.status_code)
        else:
            raise APIError(f"Server error: {error_message}", status_code=response.status_code)

    def _extract_error_message(self, response_data: Dict[str, Any]) -> str:
        """Extract error message from response data."""
        if isinstance(response_data, dict):
            return (
                response_data.get("error") or
                response_data.get("message") or
                response_data.get("detail") or
                "Unknown error"
            )
        return str(response_data)

# Global client instance
_client = APIClient()

async def make_api_request(
    endpoint: str, 
    method: str = "GET", 
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> Any:
    """Enhanced API request function with better error handling."""
    return await _client.request(method, endpoint, json_data, params)

def build_url(base_url: str, params: Dict[str, Union[str, int, None]]) -> str:
    """Build URL with query parameters (GitHub-style)."""
    from urllib.parse import urlencode
    
    # Filter out None values
    clean_params = {k: str(v) for k, v in params.items() if v is not None}
    
    if clean_params:
        query_string = urlencode(clean_params)
        return f"{base_url}?{query_string}"
    return base_url

def format_response(data: Any) -> str:
    """Enhanced response formatting with better error handling."""
    if isinstance(data, dict):
        if "error" in data:
            return f"❌ Error: {data['error']}"
        if "success" in data and not data["success"]:
            return f"❌ Failed: {data.get('message', 'Unknown error')}"
    
    try:
        return json.dumps(data, indent=2, default=str)
    except Exception as e:
        logger.warning(f"Failed to format response: {e}")
        return str(data)

def validate_email(email: str) -> bool:
    """Simple email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_id(id_value: str) -> str:
    """Validate and sanitize ID values."""
    if not id_value or not id_value.strip():
        raise ValueError("ID cannot be empty")
    
    sanitized = id_value.strip()
    if len(sanitized) < 1:
        raise ValueError("ID too short")
    
    return sanitized

def generate_id() -> str:
    """Generate a unique ID."""
    import uuid
    return str(uuid.uuid4())

async def check_api_health() -> bool:
    """Check if the API server is healthy."""
    try:
        response = await make_api_request("/")
        return isinstance(response, dict) and "message" in response
    except Exception:
        return False