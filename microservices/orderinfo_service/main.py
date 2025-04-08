from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from orderinfomanager import OrderInfoManager
import uvicorn
app = FastAPI(title="Order Info Service")
manager = OrderInfoManager()  # loads data/orderInfo.xlsx

class OrderInfo(BaseModel):
    name: str
    phone: str
    address: str
    note: Optional[str] = None
    order: str
    price: float

@app.get("/orderinfo")
def list_all_orders():
    df = manager.read_orders()
    return df.to_dict(orient="records")

@app.post("/orderinfo")
def save_order_info(data: OrderInfo):
    manager.save_order_info(
        name=data.name,
        phone=data.phone,
        address=data.address,
        note=data.note if data.note else "",
        order=data.order,
        price=data.price
    )
    return {"message": "Order info saved"}

@app.put("/orderinfo/{index}")
def update_order(index: int, data: OrderInfo):
    manager.update_order(
        index=index,
        name=data.name,
        phone=data.phone,
        address=data.address,
        note=data.note if data.note else ""
    )
    return {"message": f"Order {index} updated"}

@app.delete("/orderinfo/{index}")
def delete_order(index: int):
    manager.delete_order(index)
    return {"message": f"Order {index} deleted"}
if __name__ == "__main__":
    # OrderInfo Service runs on port 8005
    uvicorn.run(app, host="0.0.0.0", port=8005)