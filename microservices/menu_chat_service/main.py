from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import os
import uvicorn
app = FastAPI(title="Gemini Menu Chat Service")

API_KEY = "AIzaSyCI9Fzm4AEv3zPtzr5SVp1xmyOcfr1t830"
MODEL = "gemini-1.5-pro"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
MENU_FILE = "microservices/menu_chat_service/data/menu_vi.txt" 

class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
def ask_about_menu(data: ChatRequest):
    if not os.path.exists(MENU_FILE):
        raise HTTPException(status_code=500, detail="Menu file not found")

    with open(MENU_FILE, "r", encoding="utf-8") as file:
        menu_text = file.read()

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Menu nhà hàng:\n{menu_text}\n\nCâu hỏi: {data.question}"
                    }
                ]
            }
        ]
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        result = response.json()
        answer = result["candidates"][0]["content"]["parts"][0]["text"]
        return {"answer": answer}
    else:
        raise HTTPException(status_code=500, detail=f"Gemini error: {response.text}")
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8012)