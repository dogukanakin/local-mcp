# Direct REST API Client with Ollama

A minimal project where Ollama directly communicates with a FastAPI REST API (no MCP server needed).

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Services (in 2 separate terminals)

**Terminal 1: Start FastAPI Service**
```bash
python api-mcp/api_service.py
```

**Terminal 2: Start Ollama Client**
```bash
python api-mcp/client.py
```

## 💬 Usage
The client directly talks to the FastAPI REST API. Interact using natural language:
- `list all users`
- `create a user named john with email john@test.com`
- `list all posts`
- `create a post titled 'Hello World' with content 'My first post' and author_id 'user-123'`

## 🔄 How It Works
1. **FastAPI Service** (port 8001): Provides REST endpoints for users and posts
2. **Ollama Client**: Uses LlamaIndex + ReActAgent to understand natural language and call API functions directly

## 📡 Available API Endpoints
- `GET /users` - List all users
- `POST /users` - Create a new user
- `GET /posts` - List all posts  
- `POST /posts` - Create a new post
- `GET /` - Health check

## 📁 Project Structure
```
api-mcp/
├── api_service.py          # FastAPI REST API service
├── client.py              # Direct API client with Ollama
├── requirements.txt       # Dependencies
└── (legacy MCP server files - not needed for this approach)
```

## 🧪 Test the API Directly
You can also test the FastAPI service directly:
```bash
curl http://127.0.0.1:8001/users
curl -X POST http://127.0.0.1:8001/users -H "Content-Type: application/json" -d '{"id":"123","name":"test","email":"test@test.com"}'
```