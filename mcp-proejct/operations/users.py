"""Enhanced user operations for API MCP server (GitHub-style)."""

from typing import List, Dict, Any, Optional
try:
    from ..common.utils import make_api_request, build_url, validate_email, generate_id
    from ..common.types import (
        User, UserCreate, UserUpdate, ListUsersSchema, CreateUserSchema,
        UserListResponse, APIResponse
    )
    from ..common.errors import ValidationError, NotFoundError
except ImportError:
    # Fallback for direct execution
    from common.utils import make_api_request, build_url, validate_email, generate_id
    from common.types import (
        User, UserCreate, UserUpdate, ListUsersSchema, CreateUserSchema,
        UserListResponse, APIResponse
    )
    from common.errors import ValidationError, NotFoundError

# User operation schemas
class GetUserSchema:
    """Schema for getting a specific user."""
    def __init__(self, user_id: str):
        self.user_id = user_id

class UpdateUserSchema:
    """Schema for updating a user."""
    def __init__(self, user_id: str, name: Optional[str] = None, email: Optional[str] = None):
        self.user_id = user_id
        self.name = name
        self.email = email

class DeleteUserSchema:
    """Schema for deleting a user."""
    def __init__(self, user_id: str):
        self.user_id = user_id

# API Functions
async def list_users(
    page: int = 1,
    per_page: int = 10,
    search: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Lists all users with pagination and search."""
    params = {
        "page": page,
        "per_page": per_page,
        "search": search
    }
    
    # For now, just return all users (API doesn't support pagination yet)
    return await make_api_request("users", params=params)

async def get_user(user_id: str) -> Dict[str, Any]:
    """Gets a specific user by ID."""
    if not user_id:
        raise ValidationError("User ID is required")
    
    try:
        return await make_api_request(f"users/{user_id}")
    except Exception as e:
        if "404" in str(e):
            raise NotFoundError(f"User with ID '{user_id}' not found")
        raise

async def create_user(name: str, email: str) -> Dict[str, Any]:
    """Creates a new user with validation."""
    # Validate inputs
    if not name or not name.strip():
        raise ValidationError("Name is required")
    
    if not email or not email.strip():
        raise ValidationError("Email is required")
    
    if not validate_email(email):
        raise ValidationError("Invalid email format")
    
    # Prepare user data
    user_data = {
        "id": generate_id(),
        "name": name.strip(),
        "email": email.strip().lower()
    }
    
    return await make_api_request("users", method="POST", json_data=user_data)

async def update_user(
    user_id: str,
    name: Optional[str] = None,
    email: Optional[str] = None
) -> Dict[str, Any]:
    """Updates an existing user."""
    if not user_id:
        raise ValidationError("User ID is required")
    
    # Build update data
    update_data = {}
    
    if name is not None:
        if not name.strip():
            raise ValidationError("Name cannot be empty")
        update_data["name"] = name.strip()
    
    if email is not None:
        if not email.strip():
            raise ValidationError("Email cannot be empty")
        if not validate_email(email):
            raise ValidationError("Invalid email format")
        update_data["email"] = email.strip().lower()
    
    if not update_data:
        raise ValidationError("No fields to update")
    
    try:
        return await make_api_request(f"users/{user_id}", method="PUT", json_data=update_data)
    except Exception as e:
        if "404" in str(e):
            raise NotFoundError(f"User with ID '{user_id}' not found")
        raise

async def delete_user(user_id: str) -> Dict[str, Any]:
    """Deletes a user."""
    if not user_id:
        raise ValidationError("User ID is required")
    
    try:
        return await make_api_request(f"users/{user_id}", method="DELETE")
    except Exception as e:
        if "404" in str(e):
            raise NotFoundError(f"User with ID '{user_id}' not found")
        raise

async def search_users(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search users by name or email."""
    if not query or not query.strip():
        raise ValidationError("Search query is required")
    
    params = {
        "search": query.strip(),
        "limit": limit
    }
    
    return await make_api_request("users/search", params=params)

# High-level operations for MCP tools
async def list_all_users() -> str:
    """MCP tool: Lists all users and returns formatted JSON."""
    try:
        from ..common.utils import format_response
    except ImportError:
        from common.utils import format_response
    try:
        users = await list_users()
        return format_response(users)
    except Exception as e:
        try:
            from ..common.errors import format_api_error
        except ImportError:
            from common.errors import format_api_error
        return format_api_error(e)

async def create_new_user(name: str, email: str) -> str:
    """MCP tool: Creates a new user and returns formatted response."""
    try:
        from ..common.utils import format_response
    except ImportError:
        from common.utils import format_response
    try:
        user = await create_user(name, email)
        return format_response(user)
    except Exception as e:
        try:
            from ..common.errors import format_api_error
        except ImportError:
            from common.errors import format_api_error
        return format_api_error(e)