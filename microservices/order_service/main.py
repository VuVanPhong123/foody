from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from ordermanager import OrderManager
import uvicorn
app = FastAPI(title="Order Service")
manager = OrderManager()  
class OrderItem(BaseModel):
    items: Dict[str, int]

@app.get("/menu")
def get_menu():
    return manager.menu

@app.post("/orders")
def create_order(order: OrderItem):
    selected_items = {}
    for name, qty in order.items.items():
        if qty < 0:
            raise HTTPException(status_code=400, detail="Quantity must be >= 0")
        if qty == 0:
            continue  
        if name not in manager.menu:
            raise HTTPException(status_code=404, detail=f"Item '{name}' not in menu.")
        selected_items[name] = qty

    if not selected_items:
        raise HTTPException(status_code=400, detail="No items with a positive quantity.")
    
    total_price = manager.calculate_total(selected_items)
    manager.save_order(selected_items)
    return {
        "message": "Order created successfully",
        "total_price": total_price,
        "items": selected_items
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)