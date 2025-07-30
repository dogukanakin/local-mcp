"""Direct REST API Client with Ollama"""

import asyncio
import httpx
import json
from typing import List, Dict, Any, Optional
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent

# API Base URL
API_BASE_URL = "http://127.0.0.1:8001"

async def make_api_request(url: str, method: str = "GET", json_data: Optional[Dict[str, Any]] = None) -> Any:
    """Makes a direct API request to FastAPI service."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                json=json_data,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

async def list_users() -> str:
    """Lists all users from the API."""
    result = await make_api_request(f"{API_BASE_URL}/users")
    return json.dumps(result, indent=2)

async def create_user(name: str, email: str) -> str:
    """Creates a new user via the API."""
    import uuid
    user_data = {"id": str(uuid.uuid4()), "name": name, "email": email}
    result = await make_api_request(f"{API_BASE_URL}/users", method="POST", json_data=user_data)
    return json.dumps(result, indent=2)

async def list_posts() -> str:
    """Lists all posts from the API."""
    result = await make_api_request(f"{API_BASE_URL}/posts")
    return json.dumps(result, indent=2)

async def create_post(title: str, content: str, author_id: str) -> str:
    """Creates a new post via the API."""
    import uuid
    post_data = {"id": str(uuid.uuid4()), "title": title, "content": content, "author_id": author_id}
    result = await make_api_request(f"{API_BASE_URL}/posts", method="POST", json_data=post_data)
    return json.dumps(result, indent=2)

async def main():
    # Initialize Ollama
    Settings.llm = Ollama(model="llama3.2", request_timeout=120.0)
    
    # Create tools that directly call the REST API
    tools = [
        FunctionTool.from_defaults(async_fn=list_users),
        FunctionTool.from_defaults(async_fn=create_user),
        FunctionTool.from_defaults(async_fn=list_posts),
        FunctionTool.from_defaults(async_fn=create_post),
    ]

    SYSTEM_PROMPT = """\
You are a helpful AI assistant that manages users and posts via a REST API.
You can list and create users and posts by calling the API directly.

Available functions:
- list_users(): Get all users
- create_user(name, email): Create a new user
- list_posts(): Get all posts  
- create_post(title, content, author_id): Create a new post

When users ask for something, use the appropriate function to call the REST API.
"""

    # Create agent with direct API tools
    agent = ReActAgent.from_tools(
        tools=tools,
        llm=Settings.llm,
        system_prompt=SYSTEM_PROMPT,
        verbose=True
    )
    
    print("🚀 Direct REST API Client Ready!")
    print("💡 This client talks directly to the FastAPI service (no MCP server needed)")
    print("Example: 'list all users' or 'create a user named test with email test@test.com'")
    
    while True:
        user_input = input("💬 Your message: ")
        if user_input.lower() in ['exit', 'quit']:
            print("👋 Goodbye!")
            break
        
        try:
            response = await agent.achat(user_input)
            print(f"🤖 Response: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())