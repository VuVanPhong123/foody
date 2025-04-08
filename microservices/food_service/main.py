from fastapi import FastAPI, HTTPException
from foodmanager import FoodManager
from pydantic import BaseModel
from typing import Optional
import uvicorn
app = FastAPI(title="Food (Menu) Service")
manager = FoodManager()  # loads data/food.xlsx

@app.get("/menu")
def list_menu():
    return manager.menu_items

class FoodIn(BaseModel):
    name: str
    price: int
    image: Optional[str] = None

@app.post("/menu")
def add_menu_item(item: FoodIn):
    # If you want to append to food.xlsx, do so here (not fully implemented)
    return {"message": f"Added {item.name} to menu (placeholder)."}

if __name__ == "__main__":
    # Food Service runs on port 8003
    uvicorn.run(app, host="0.0.0.0", port=8003)