"""Enhanced data types and models for API MCP server (GitHub-style)."""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Configuration for all models
class BaseAPIModel(BaseModel):
    """Base model with common configuration."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )

# --- Base Response Models ---
class APIResponse(BaseAPIModel):
    """Standard API response wrapper."""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseAPIModel):
    """Error response model."""
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# --- User Models ---
class UserBase(BaseAPIModel):
    """Base user fields."""
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: str = Field(..., description="User's email address")

class UserCreate(UserBase):
    """Schema for creating a user."""
    pass

class UserUpdate(BaseAPIModel):
    """Schema for updating a user."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = None

class User(UserBase):
    """Complete user model."""
    id: str = Field(..., description="Unique user identifier")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# --- Post Models ---
class PostStatus(str, Enum):
    """Post status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class PostBase(BaseAPIModel):
    """Base post fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Post title")
    content: str = Field(..., min_length=1, description="Post content")

class PostCreate(PostBase):
    """Schema for creating a post."""
    author_id: str = Field(..., description="ID of the post author")
    status: PostStatus = PostStatus.DRAFT

class PostUpdate(BaseAPIModel):
    """Schema for updating a post."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    status: Optional[PostStatus] = None

class Post(PostBase):
    """Complete post model."""
    id: str = Field(..., description="Unique post identifier")
    author_id: str = Field(..., description="ID of the post author")
    status: PostStatus = PostStatus.DRAFT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# --- List Response Models ---
class UserListResponse(BaseAPIModel):
    """Response for user list operations."""
    users: List[User]
    total: int
    page: int = 1
    per_page: int = 10

class PostListResponse(BaseAPIModel):
    """Response for post list operations."""
    posts: List[Post]
    total: int
    page: int = 1
    per_page: int = 10

# --- Operation Input Schemas (GitHub-style) ---
class ListUsersSchema(BaseAPIModel):
    """Schema for listing users."""
    page: Optional[int] = Field(1, ge=1, description="Page number")
    per_page: Optional[int] = Field(10, ge=1, le=100, description="Items per page")
    search: Optional[str] = Field(None, description="Search query")

class ListPostsSchema(BaseAPIModel):
    """Schema for listing posts."""
    page: Optional[int] = Field(1, ge=1, description="Page number")
    per_page: Optional[int] = Field(10, ge=1, le=100, description="Items per page")
    author_id: Optional[str] = Field(None, description="Filter by author ID")
    status: Optional[PostStatus] = Field(None, description="Filter by status")

class CreateUserSchema(BaseAPIModel):
    """Schema for user creation operations."""
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")

class CreatePostSchema(BaseAPIModel):
    """Schema for post creation operations."""
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post content")
    author_id: str = Field(..., description="Author ID")
    status: PostStatus = Field(PostStatus.DRAFT, description="Post status")