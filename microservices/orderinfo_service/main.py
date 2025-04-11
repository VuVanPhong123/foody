from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import os
import uvicorn

app = FastAPI(title="Order Info Service")

DATA_PATH = "microservices/orderinfo_service/data/orderInfo.xlsx"
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

class OrderInfo(BaseModel):
    name: str
    phone: str
    address: str
    note: Optional[str] = None
    order: str
    price: float

# --- File manager functions ---
def read_orders():
    if os.path.exists(DATA_PATH):
        return pd.read_excel(DATA_PATH)
    return pd.DataFrame(columns=["name", "phone", "address", "note", "order", "price"])

def save_order(info: OrderInfo):
    df = read_orders()
    df.loc[len(df)] = [info.name, info.phone, info.address, info.note or "", info.order, info.price]
    df.to_excel(DATA_PATH, index=False)

def update_order(index: int, updated: OrderInfo):
    df = read_orders()
    if index < 0 or index >= len(df):
        raise IndexError("Invalid index")
    df.loc[index, ["name", "phone", "address", "note", "order", "price"]] = [
        updated.name, updated.phone, updated.address, updated.note or "", updated.order, updated.price
    ]
    df.to_excel(DATA_PATH, index=False)

def delete_order(index: int):
    df = read_orders()
    if index < 0 or index >= len(df):
        raise IndexError("Invalid index")
    df = df.drop(index).reset_index(drop=True)
    df.to_excel(DATA_PATH, index=False)

# --- API endpoints ---
@app.get("/orderinfo")
def list_orders():
    df = read_orders()
    return df.to_dict(orient="records")

@app.post("/orderinfo")
def create_order(info: OrderInfo):
    try:
        save_order(info)
        return {"message": "Order saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/orderinfo/{index}")
def modify_order(index: int, info: OrderInfo):
    try:
        update_order(index, info)
        return {"message": f"Order {index} updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/orderinfo/{index}")
def remove_order(index: int):
    try:
        delete_order(index)
        return {"message": f"Order {index} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
