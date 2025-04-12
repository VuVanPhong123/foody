from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
import uvicorn

app = FastAPI(title="Order Service")

FOOD_FILE = "microservices/food_service/data/food.xlsx"

class OrderRequest(BaseModel):
    items: dict  # e.g., {"Pizza": 2, "Burger": 1}

def load_menu():
    if not os.path.exists(FOOD_FILE):
        return {}
    try:
        df = pd.read_excel(FOOD_FILE)
        return {str(row['food']).strip(): int(row['price']) for _, row in df.iterrows()}
    except Exception as e:
        print("Error loading food.xlsx:", e)
        return {}

@app.post("/orders")
def calculate_order(data: OrderRequest):
    try:
        menu = load_menu()
        total = 0
        for name, qty in data.items.items():
            if qty > 0:
                price = menu.get(name, 0)
                total += price * qty
        return {"total_price": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/menu")
def get_menu():
    try:
        menu = load_menu()
        return menu
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
