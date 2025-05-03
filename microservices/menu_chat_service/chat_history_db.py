import sqlite3
import os
from datetime import datetime
import json

class ChatHistoryDB:
    DB_PATH = "microservices/menu_chat_service/data/chat_history.db"
    
    def __init__(self):
        os.makedirs(os.path.dirname(self.DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(self.DB_PATH, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        # Table for individual Q&A pairs
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_question TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        ''')
        
        # Table for complete conversations
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            session_id TEXT PRIMARY KEY,
            conversation_data TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        ''')
        
        self.conn.commit()
    
    def add_chat(self, question, answer):
        timestamp = datetime.now().isoformat()
        self.conn.execute(
            "INSERT INTO chat_history (user_question, ai_response, timestamp) VALUES (?, ?, ?)",
            (question, answer, timestamp)
        )
        self.conn.commit()
    
    def add_full_conversation(self, session_id, conversation_json):
        timestamp = datetime.now().isoformat()
        self.conn.execute(
            "INSERT OR REPLACE INTO conversations (session_id, conversation_data, timestamp) VALUES (?, ?, ?)",
            (session_id, conversation_json, timestamp)
        )
        self.conn.commit()
    
    def get_all_chats(self):
        cursor = self.conn.execute(
            "SELECT id, user_question, ai_response, timestamp FROM chat_history ORDER BY timestamp DESC"
        )
        results = []
        for row in cursor:
            results.append({
                "id": row[0],
                "question": row[1],
                "answer": row[2],
                "timestamp": row[3]
            })
        return results
    
    def get_recent_chats(self, limit=10):
        cursor = self.conn.execute(
            "SELECT id, user_question, ai_response, timestamp FROM chat_history ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        results = []
        for row in cursor:
            results.append({
                "id": row[0],
                "question": row[1],
                "answer": row[2],
                "timestamp": row[3]
            })
        return results
    
    def get_conversations(self):
        cursor = self.conn.execute(
            "SELECT session_id, conversation_data, timestamp FROM conversations ORDER BY timestamp DESC"
        )
        results = []
        for row in cursor:
            results.append({
                "session_id": row[0],
                "conversation": json.loads(row[1]),
                "timestamp": row[2]
            })
        return results
    
    def clear_all_chats(self):
        self.conn.execute("DELETE FROM chat_history")
        self.conn.execute("DELETE FROM conversations")
        self.conn.commit() 