from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import aiosqlite
import asyncio
from datetime import datetime
import os
import uvicorn

DB_PATH = "microservices/chat_service/chat.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

app = FastAPI(title="Chat Service – SQLite")

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS messages (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    sender   TEXT    NOT NULL,        -- 'owner' | 'customer'
    content  TEXT    NOT NULL,
    ts       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

async def _get_db():
    db = await aiosqlite.connect(DB_PATH)
    await db.execute(CREATE_SQL)
    return db


class ChatMessage(BaseModel):
    sender: str  
    message: str


@app.post("/chat", status_code=201)
async def send_message(msg: ChatMessage):
    if msg.sender not in {"owner", "customer"}:
        raise HTTPException(status_code=400, detail="Invalid sender")

    db = await _get_db()
    await db.execute(
        "INSERT INTO messages (sender, content) VALUES (?, ?)",
        (msg.sender, msg.message),
    )
    await db.commit()
    await db.close()
    return {"status": "ok"}


@app.get("/chat")
async def get_chat(after_id: int | None = Query(None, description="return rows with id > after_id")):
    db = await _get_db()
    if after_id is None:
        rows = await db.execute_fetchall("SELECT * FROM messages ORDER BY id")
    else:
        rows = await db.execute_fetchall(
            "SELECT * FROM messages WHERE id > ? ORDER BY id", (after_id,)
        )
    await db.close()

    result = []
    for rid, sender, content, ts in rows:
        result.append(
            {
                "id": rid,
                "owner": content if sender == "owner" else "",
                "customer": content if sender == "customer" else "",
                "ts": ts,
            }
        )
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)
