"""Enhanced post operations for API MCP server (GitHub-style)."""

from typing import List, Dict, Any, Optional
try:
    from ..common.utils import make_api_request, build_url, generate_id
    from ..common.types import (
        Post, PostCreate, PostUpdate, PostStatus, ListPostsSchema, CreatePostSchema,
        PostListResponse, APIResponse
    )
    from ..common.errors import ValidationError, NotFoundError
except ImportError:
    # Fallback for direct execution
    from common.utils import make_api_request, build_url, generate_id
    from common.types import (
        Post, PostCreate, PostUpdate, PostStatus, ListPostsSchema, CreatePostSchema,
        PostListResponse, APIResponse
    )
    from common.errors import ValidationError, NotFoundError

# Post operation schemas
class GetPostSchema:
    """Schema for getting a specific post."""
    def __init__(self, post_id: str):
        self.post_id = post_id

class UpdatePostSchema:
    """Schema for updating a post."""
    def __init__(
        self,
        post_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        status: Optional[PostStatus] = None
    ):
        self.post_id = post_id
        self.title = title
        self.content = content
        self.status = status

class DeletePostSchema:
    """Schema for deleting a post."""
    def __init__(self, post_id: str):
        self.post_id = post_id

# API Functions
async def list_posts(
    page: int = 1,
    per_page: int = 10,
    author_id: Optional[str] = None,
    status: Optional[PostStatus] = None
) -> List[Dict[str, Any]]:
    """Lists all posts with pagination and filtering."""
    params = {
        "page": page,
        "per_page": per_page,
        "author_id": author_id,
        "status": status.value if status else None
    }
    
    # For now, just return all posts (API doesn't support filtering yet)
    return await make_api_request("posts", params=params)

async def get_post(post_id: str) -> Dict[str, Any]:
    """Gets a specific post by ID."""
    if not post_id:
        raise ValidationError("Post ID is required")
    
    try:
        return await make_api_request(f"posts/{post_id}")
    except Exception as e:
        if "404" in str(e):
            raise NotFoundError(f"Post with ID '{post_id}' not found")
        raise

async def create_post(
    title: str,
    content: str,
    author_id: str,
    status: PostStatus = PostStatus.DRAFT
) -> Dict[str, Any]:
    """Creates a new post with validation."""
    # Validate inputs
    if not title or not title.strip():
        raise ValidationError("Title is required")
    
    if not content or not content.strip():
        raise ValidationError("Content is required")
    
    if not author_id or not author_id.strip():
        raise ValidationError("Author ID is required")
    
    if len(title.strip()) > 200:
        raise ValidationError("Title too long (max 200 characters)")
    
    # Prepare post data
    post_data = {
        "id": generate_id(),
        "title": title.strip(),
        "content": content.strip(),
        "author_id": author_id.strip(),
        "status": status.value if isinstance(status, PostStatus) else status
    }
    
    return await make_api_request("posts", method="POST", json_data=post_data)

async def update_post(
    post_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    status: Optional[PostStatus] = None
) -> Dict[str, Any]:
    """Updates an existing post."""
    if not post_id:
        raise ValidationError("Post ID is required")
    
    # Build update data
    update_data = {}
    
    if title is not None:
        if not title.strip():
            raise ValidationError("Title cannot be empty")
        if len(title.strip()) > 200:
            raise ValidationError("Title too long (max 200 characters)")
        update_data["title"] = title.strip()
    
    if content is not None:
        if not content.strip():
            raise ValidationError("Content cannot be empty")
        update_data["content"] = content.strip()
    
    if status is not None:
        if isinstance(status, PostStatus):
            update_data["status"] = status.value
        else:
            update_data["status"] = status
    
    if not update_data:
        raise ValidationError("No fields to update")
    
    try:
        return await make_api_request(f"posts/{post_id}", method="PUT", json_data=update_data)
    except Exception as e:
        if "404" in str(e):
            raise NotFoundError(f"Post with ID '{post_id}' not found")
        raise

async def delete_post(post_id: str) -> Dict[str, Any]:
    """Deletes a post."""
    if not post_id:
        raise ValidationError("Post ID is required")
    
    try:
        return await make_api_request(f"posts/{post_id}", method="DELETE")
    except Exception as e:
        if "404" in str(e):
            raise NotFoundError(f"Post with ID '{post_id}' not found")
        raise

async def publish_post(post_id: str) -> Dict[str, Any]:
    """Publishes a post (changes status to PUBLISHED)."""
    return await update_post(post_id, status=PostStatus.PUBLISHED)

async def archive_post(post_id: str) -> Dict[str, Any]:
    """Archives a post (changes status to ARCHIVED)."""
    return await update_post(post_id, status=PostStatus.ARCHIVED)

async def get_posts_by_author(author_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get all posts by a specific author."""
    if not author_id:
        raise ValidationError("Author ID is required")
    
    return await list_posts(per_page=limit, author_id=author_id)

async def search_posts(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search posts by title or content."""
    if not query or not query.strip():
        raise ValidationError("Search query is required")
    
    params = {
        "search": query.strip(),
        "limit": limit
    }
    
    return await make_api_request("posts/search", params=params)

# High-level operations for MCP tools
async def list_all_posts() -> str:
    """MCP tool: Lists all posts and returns formatted JSON."""
    try:
        from ..common.utils import format_response
    except ImportError:
        from common.utils import format_response
    try:
        posts = await list_posts()
        return format_response(posts)
    except Exception as e:
        try:
            from ..common.errors import format_api_error
        except ImportError:
            from common.errors import format_api_error
        return format_api_error(e)

async def create_new_post(title: str, content: str, author_id: str) -> str:
    """MCP tool: Creates a new post and returns formatted response."""
    try:
        from ..common.utils import format_response
    except ImportError:
        from common.utils import format_response
    try:
        post = await create_post(title, content, author_id)
        return format_response(post)
    except Exception as e:
        try:
            from ..common.errors import format_api_error
        except ImportError:
            from common.errors import format_api_error
        return format_api_error(e)