"""
Minimal FastAPI Dummy REST API
A simple REST API with users and posts endpoints for prototyping.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import uuid

# Initialize FastAPI app
app = FastAPI(
    title="Minimal Dummy REST API",
    description="A minimal REST API for prototyping with users and posts",
    version="1.0.0"
)

# --- Pydantic Models ---
class User(BaseModel):
    id: str
    name: str
    email: str

class Post(BaseModel):
    id: str
    title: str
    content: str
    author_id: str

# --- In-memory Storage ---
users_db: List[User] = []
posts_db: List[Post] = []

# Helper to generate ID
def generate_id() -> str:
    return str(uuid.uuid4())

# --- User Endpoints ---
@app.get("/users", response_model=List[User])
async def get_users():
    return users_db

@app.post("/users", response_model=User)
async def create_user(user: User):
    users_db.append(user)
    return user

# --- Post Endpoints ---
@app.get("/posts", response_model=List[Post])
async def get_posts():
    return posts_db

@app.post("/posts", response_model=Post)
async def create_post(post: Post):
    posts_db.append(post)
    return post
    
# --- Root Endpoint ---
@app.get("/")
async def root():
    return {"message": "Minimal API is running"}
    
if __name__ == "__main__":
    print("🚀 Starting Minimal FastAPI REST API...")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
