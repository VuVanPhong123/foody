from fastapi import FastAPI, HTTPException
from foodmanager import FoodManager
from pydantic import BaseModel
from typing import Optional
import uvicorn
app = FastAPI(title="Food (Menu) Service")
manager = FoodManager()  

@app.get("/menu")
def list_menu():
    return manager.menu_items

class FoodIn(BaseModel):
    name: str
    price: int
    image: Optional[str] = None

@app.post("/menu")
def add_menu_item(item: FoodIn):
    return {"message": f"Added {item.name} to menu (placeholder)."}

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8003)