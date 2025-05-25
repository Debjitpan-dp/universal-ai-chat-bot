from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import json
import asyncio
from datetime import datetime
import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import Ollama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Universal AI Chat API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for HTML frontend
app.mount("/static", StaticFiles(directory="frontend/html"), name="static")

# In-memory storage (in production, use a proper database)
conversations: Dict[str, Dict] = {}
user_settings: Dict[str, Dict] = {}

# Models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    llm_type: str = "chatgpt"
    api_key: str
    system_prompt: Optional[str] = None
    use_context: bool = True
    use_websearch: bool = False
    website_url: Optional[str] = None

class ConversationResponse(BaseModel):
    conversation_id: str
    response: str
    timestamp: str

class ConversationHistory(BaseModel):
    conversation_id: str
    title: str
    messages: List[Dict[str, Any]]
    created_at: str
    updated_at: str

class UserSettings(BaseModel):
    user_id: str
    default_llm: str = "chatgpt"
    default_system_prompt: Optional[str] = None
    api_keys: Dict[str, str] = {}

# Utility functions
def create_llm_instance(llm_type: str, api_key: str) -> Any:
    """Create LLM instance based on type and API key"""
    try:
        if llm_type.lower() == "chatgpt":
            return ChatOpenAI(
                openai_api_key=api_key,
                model_name="gpt-3.5-turbo",
                temperature=0.7
            )
        elif llm_type.lower() == "claude":
            return ChatAnthropic(
                anthropic_api_key=api_key,
                model="claude-3-7-sonnet-20250219",
                temperature=0.7
            )
        elif llm_type.lower() == "llama3":
            # Assuming Ollama is running locally
            return Ollama(model="llama3")
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")
    except Exception as e:
        logger.error(f"Error creating LLM instance: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to create LLM instance: {str(e)}")

def scrape_website(url: str) -> str:
    """Scrape website content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit text length
        return text[:5000] if len(text) > 5000 else text
        
    except Exception as e:
        logger.error(f"Error scraping website {url}: {e}")
        return f"Error scraping website: {str(e)}"

def perform_web_search(query: str) -> str:
    """Perform web search using DuckDuckGo"""
    try:
        search = DuckDuckGoSearchRun()
        results = search.run(query)
        return results
    except Exception as e:
        logger.error(f"Error performing web search: {e}")
        return f"Error performing web search: {str(e)}"

# API Routes
@app.get("/")
async def root():
    """Root endpoint - serve HTML frontend"""
    return HTMLResponse(open("frontend/html/index.html").read())

@app.post("/chat", response_model=ConversationResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint"""
    try:
        # Generate conversation ID if not provided
        if not request.conversation_id:
            request.conversation_id = str(uuid.uuid4())
        logger.info(f"Received chat request: {request.message} (Conversation ID: {request.conversation_id})")
            
        # Initialize conversation if new
        if request.conversation_id not in conversations:
            conversations[request.conversation_id] = {
                "conversation_id": request.conversation_id,
                "title": request.message[:50] + "..." if len(request.message) > 50 else request.message,
                "messages": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        logger.info(f"Using conversation ID: {request.conversation_id}")
        
        # Create LLM instance
        llm = create_llm_instance(request.llm_type, request.api_key)
        
        # Prepare messages
        messages = []
        
        # Add system prompt if provided
        if request.system_prompt:
            # messages.append(SystemMessage(content=request.system_prompt))
            messages.append({"role": "system", "content": request.system_prompt})
        logger.info(f"System prompt added: {request.system_prompt}")
        
        # Add conversation context if enabled
        if request.use_context:
            conv_messages = conversations[request.conversation_id]["messages"]
            for msg in conv_messages[-10:]:  # Limit context to last 10 messages
                if msg["role"] == "user":
                    # messages.append(HumanMessage(content=msg["content"]))
                    messages.append({"role": "user", "content": msg["content"]})
                elif msg["role"] == "assistant":
                    # messages.append(AIMessage(content=msg["content"]))
                    messages.append({"role": "assistant", "content": msg["content"]})

        logger.info(f"Messages prepared for LLM: {messages}")
        
        # Handle website scraping
        user_message = request.message
        if request.website_url:
            scraped_content = scrape_website(request.website_url)
            user_message = f"Based on the following website content, {request.message}\n\nWebsite content:\n{scraped_content}"
        
        # Handle web search
        if request.use_websearch:
            search_results = perform_web_search(request.message)
            user_message = f"{request.message}\n\nWeb search results:\n{search_results}"
        
        # Add current user message
        # messages.append(HumanMessage(content=user_message))
        messages.append({"role": "user", "content": user_message})
        
        # Get LLM response
        response = await asyncio.to_thread(llm.invoke, messages)
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Store messages in conversation
        conversations[request.conversation_id]["messages"].extend([
            {
                "role": "user",
                "content": request.message,
                "timestamp": datetime.now().isoformat()
            },
            {
                "role": "assistant", 
                "content": response_text,
                "timestamp": datetime.now().isoformat()
            }
        ])
        conversations[request.conversation_id]["updated_at"] = datetime.now().isoformat()
        
        return ConversationResponse(
            conversation_id=request.conversation_id,
            response=response_text,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations", response_model=List[ConversationHistory])
async def get_conversations():
    """Get all conversation histories"""
    return list(conversations.values())

@app.get("/conversations/{conversation_id}", response_model=ConversationHistory)
async def get_conversation(conversation_id: str):
    """Get specific conversation"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversations[conversation_id]

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    del conversations[conversation_id]
    return {"message": "Conversation deleted successfully"}

@app.post("/settings")
async def save_user_settings(settings: UserSettings):
    """Save user settings"""
    user_settings[settings.user_id] = settings.dict()
    return {"message": "Settings saved successfully"}

@app.get("/settings/{user_id}", response_model=UserSettings)
async def get_user_settings(user_id: str):
    """Get user settings"""
    if user_id not in user_settings:
        # Return default settings
        return UserSettings(user_id=user_id)
    return UserSettings(**user_settings[user_id])

# WebSocket for real-time chat
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process the message and send response
            # This is a simplified version - in practice, you'd process the chat request here
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)