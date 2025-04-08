from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from cartmanager import CartManager
import uvicorn
app = FastAPI(title="Cart Service")
manager = CartManager() 

class CartItems(BaseModel):
    items: Dict[str, int]
    total_price: float

@app.get("/cart")
def read_cart():
    df = manager.read_cart()
    return df.to_dict(orient="records")

@app.post("/cart")
def add_cart(cart: CartItems):
    selected_quantities = cart.items
    manager.write_cart(selected_quantities, [])  
    return {"message": "Cart updated"}

@app.delete("/cart")
def clear_cart():
    manager.clear_cart()
    return {"message": "Cart cleared"}
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)