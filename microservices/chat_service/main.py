from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
import uvicorn

app = FastAPI(title="Chat Service")

CHAT_FILE = "microservices/chat_service/data/chat.xlsx"
os.makedirs(os.path.dirname(CHAT_FILE), exist_ok=True)

class ChatMessage(BaseModel):
    sender: str  
    message: str

@app.post("/chat")
def send_message(msg: ChatMessage):
    if msg.sender not in ["owner", "customer"]:
        raise HTTPException(status_code=400, detail="Invalid sender")

    if os.path.exists(CHAT_FILE):
        df = pd.read_excel(CHAT_FILE)
    else:
        df = pd.DataFrame(columns=["owner", "customer"])

    if msg.sender == "owner":
        new_row = {"owner": msg.message, "customer": ""}
    else:
        new_row = {"owner": "", "customer": msg.message}

    df.loc[len(df)] = new_row
    df.to_excel(CHAT_FILE, index=False)
    return {"message": "Message saved"}

@app.get("/chat")
def get_chat():
    if not os.path.exists(CHAT_FILE):
        return []
    df = pd.read_excel(CHAT_FILE).fillna("")
    return df.to_dict(orient="records")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)
