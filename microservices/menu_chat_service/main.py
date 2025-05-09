from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import requests
import json
import os
import uvicorn
from chat_history_db import ChatHistoryDB
from google import genai
from google.genai.types import GenerateContentConfig
import uuid
from typing import Dict, Optional, List
from vector_store import MenuVectorStore

app = FastAPI(title="Gemini Menu Chat Service")

API_KEY = "AIzaSyCI9Fzm4AEv3zPtzr5SVp1xmyOcfr1t830"
MODEL = "models/gemini-1.5-pro"  # Updated to use correct model format
EMBEDDING_MODEL = "models/embedding-001"
MENU_FILE = "microservices/menu_chat_service/data/menu_vi.txt" 

# Initialize chat history database
chat_db = ChatHistoryDB()
import pathlib
with open(pathlib.Path(__file__).parent / "prompt.text", "r", encoding="utf-8") as file:
    prompt = file.read()

# Initialize the Google Generative AI client
client = genai.Client(api_key=API_KEY)

# Initialize vector store for RAG
vector_store = MenuVectorStore(api_key=API_KEY, model=EMBEDDING_MODEL)
try:
    num_items = vector_store.load_menu_data(MENU_FILE)
    print(f"Loaded {num_items} menu items into vector store")
except Exception as e:
    print(f"Error initializing vector store: {e}")

# Store active chat sessions
active_sessions: Dict[str, genai.chats.Chat] = {}

# Read menu once to use in all chat sessions
menu_text = ""
if os.path.exists(MENU_FILE):
    with open(MENU_FILE, "r", encoding="utf-8") as file:
        menu_text = file.read()

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    use_rag: Optional[bool] = True

class SessionResponse(BaseModel):
    session_id: str

def get_or_create_chat_session(session_id: Optional[str] = None) -> tuple:
    """Get existing chat session or create a new one"""
    is_new = False
    
    if not session_id or session_id not in active_sessions:
        session_id = str(uuid.uuid4())
        # Create new chat session
        chat = client.chats.create(model="gemini-2.0-flash", config=GenerateContentConfig(system_instruction=prompt))
        active_sessions[session_id] = chat
        is_new = True
        
    return active_sessions[session_id], session_id, is_new

@app.post("/chat")
def ask_about_menu(data: ChatRequest):
    # Get or create chat session for this client
    chat, session_id, is_new = get_or_create_chat_session(data.session_id)
    
    try:
        # If using RAG, retrieve relevant context
        if data.use_rag:
            relevant_items = vector_store.search(data.question, top_k=3)
            # Extract just the text content from the search results
            context = "\n\n".join([str(item[0]) for item in relevant_items])
            prompt = f"""Use the following menu items to answer the question:
            
{context}

Question: {data.question}

Answer the question based on the menu information provided above. If the information isn't in the provided menu items, say you don't have that information."""
        else:
            # Traditional approach with full menu
            prompt = f"""Menu information:
{menu_text}

Question: {data.question}

Answer the question based on the menu information."""
        
        # Send the user's question to the chat session
        response = chat.send_message(prompt)
        answer = response.text
        
        # Save to chat history
        chat_db.add_chat(data.question, answer)
        
        return {"answer": answer, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")

@app.post("/chat/end")
def end_chat_session(data: ChatRequest):
    """End a chat session and save the complete conversation"""
    if not data.session_id or data.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get the chat session
    chat = active_sessions[data.session_id]
    
    # Extract conversation history
    history = []
    for message in chat.get_history():
        text = message.parts[0].text
        role = message.role
        history.append({"role": role, "content": text})
    
    # Save complete conversation history to database
    if history:
        # You may want to modify the chat_db to support storing complete conversations
        chat_db.add_full_conversation(data.session_id, json.dumps(history))
    
    # Remove from active sessions
    del active_sessions[data.session_id]
    
    return {"message": "Chat session ended and saved"}

@app.post("/chat/start")
def start_new_chat():
    """Start a new chat session"""
    _, session_id, _ = get_or_create_chat_session()
    return {"session_id": session_id}

@app.get("/chat/history")
def get_chat_history():
    return chat_db.get_all_chats()

@app.get("/chat/history/recent")
def get_recent_chats(limit: int = 10):
    return chat_db.get_recent_chats(limit)

@app.delete("/chat/history")
def clear_chat_history():
    chat_db.clear_all_chats()
    return {"message": "Chat history cleared"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8012)