import os
from typing import List, Tuple, Dict, Optional
from langchain_openrouter import OpenRouterLLM
from langchain.prompts import PromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from datetime import datetime

path = os.path.dirname(__file__)

class BufferMemory:
    def __init__(self, max_size=5):
        self.max_size = max_size
        self.buffer: List[Dict] = []
        self.current_state = "INITIAL"
        self.context = {}
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history"""
        timestamp = datetime.now().isoformat()
        if len(self.buffer) >= self.max_size:
            self.buffer.pop(0)
        
        self.buffer.append({
            "role": role,
            "content": content,
            "timestamp": timestamp,
            "state": self.current_state
        })
    
    def get_conversation_history(self) -> List[Dict]:
        return self.buffer
    
    def clear(self):
        """Clear the conversation history"""
        self.buffer = []
        self.current_state = "INITIAL"
        self.context = {}
    
    def set_state(self, state: str):
        """Update the conversation state"""
        self.current_state = state
    
    def update_context(self, key: str, value: any):
        """Update the conversation context"""
        self.context[key] = value

class Agent:
    def __init__(self):
        self.vector_store_id = None
        self.memory = BufferMemory()
        self.initialize()
        self.llm = OpenRouterLLM(
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url="https://openrouter.ai/api",
            model="google/gemini-2.0-flash-exp:free",
        )
        
        # Load system prompt
        try:
            with open(os.path.join(path, 'prompt.text'), 'r', encoding='utf-8') as f:
                self.system_prompt = f.read()
        except Exception as e:
            print(f"Error loading system prompt: {e}")
            self.system_prompt = "You are a helpful AI assistant."
    
    def initialize(self):
        try:
            from dotenv import load_dotenv
            load_dotenv(os.path.join(path, 'api.env'))
        except ImportError:
            raise ImportError("Please install the 'dotenv' package to use this feature.")
        except Exception as e:
            raise Exception(f"Unexpected error loading .env: {e}")

        if "OPENROUTER_API_KEY" not in os.environ:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables.")

    def chat(self, message: str) -> str:
        """Process a chat message with memory state management"""
        # Add user message to memory
        self.memory.add_message("user", message)
        
        # Prepare conversation history
        messages = [SystemMessage(content=self.system_prompt)]
        
        # Add conversation history
        for msg in self.memory.get_conversation_history():
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        try:
            # Get response from LLM
            response = self.llm.invoke(messages)
            
            # Add assistant response to memory
            self.memory.add_message("assistant", response)
            
            return response
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            self.memory.add_message("system", error_msg)
            return error_msg
    
    def clear_conversation(self):
        """Clear the conversation history"""
        self.memory.clear()
    
    def get_conversation_state(self) -> str:
        """Get current conversation state"""
        return self.memory.current_state
    
    def set_conversation_state(self, state: str):
        """Set conversation state"""
        self.memory.set_state(state)
    
    def get_context(self) -> Dict:
        """Get conversation context"""
        return self.memory.context

from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

app = FastAPI(title="AI Service")
agent = Agent()
class ChatRequest(BaseModel):
    message: str
    role: str = "user"
    converstation: Optional[List[Dict]] = None

@app.post('/chat')
def chat(message: ChatRequest):
    if message.converstation:
        agent.memory.buffer = message.converstation
    response = agent.chat(message.message)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8013)