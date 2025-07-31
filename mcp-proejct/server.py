"""Minimal API MCP Server"""

import asyncio
import argparse
from mcp.server.fastmcp import FastMCP

# Use absolute imports when running as module
try:
    from .common.errors import format_api_error
    from .common.utils import format_response
    from .operations import users, posts
except ImportError:
    # Fallback for direct execution
    from common.errors import format_api_error
    from common.utils import format_response
    from operations import users, posts

mcp = FastMCP('api-mcp-server-minimal')

# --- User Tools ---
@mcp.tool()
def list_users() -> str:
    """Lists all users."""
    try:
        result = asyncio.run(users.list_users())
        return format_response(result)
    except Exception as e:
        return format_api_error(e)

@mcp.tool()
def create_user(name: str, email: str) -> str:
    """Creates a new user."""
    try:
        result = asyncio.run(users.create_user(name, email))
        return format_response(result)
    except Exception as e:
        return format_api_error(e)

# --- Post Tools ---
@mcp.tool()
def list_posts() -> str:
    """Lists all posts."""
    try:
        result = asyncio.run(posts.list_posts())
        return format_response(result)
    except Exception as e:
        return format_api_error(e)

@mcp.tool()
def create_post(title: str, content: str, author_id: str) -> str:
    """Creates a new post."""
    try:
        result = asyncio.run(posts.create_post(title, content, author_id))
        return format_response(result)
    except Exception as e:
        return format_api_error(e)

if __name__ == "__main__":
    print("🚀 Starting API MCP Server...")
    print("💡 This server exposes user and post management tools via MCP")
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type", type=str, default="sse", choices=["sse", "stdio"]
    )
    
    args = parser.parse_args()
    mcp.run(args.server_type)