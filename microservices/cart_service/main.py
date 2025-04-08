from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from cartmanager import CartManager
import uvicorn
app = FastAPI(title="Cart Service")
manager = CartManager()  # loads data/cart.xlsx

class CartItems(BaseModel):
    items: Dict[str, int]
    total_price: float

@app.get("/cart")
def read_cart():
    df = manager.read_cart()
    return df.to_dict(orient="records")

@app.post("/cart")
def add_cart(cart: CartItems):
    # You might need to pass a list of menu items with prices, or keep that logic in the manager
    selected_quantities = cart.items
    # The manager's write_cart expects (selected_quantities, menu_items).
    # For simplicity:
    manager.write_cart(selected_quantities, [])  # placeholder for menu items if needed
    return {"message": "Cart updated"}

@app.delete("/cart")
def clear_cart():
    manager.clear_cart()
    return {"message": "Cart cleared"}
if __name__ == "__main__":
    # Cart Service runs on port 8004
    uvicorn.run(app, host="0.0.0.0", port=8004)