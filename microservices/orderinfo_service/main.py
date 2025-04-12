from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import os
import uvicorn

app = FastAPI(title="Order Info Service")

DATA_PATH = "microservices/shared_data/orderInfo.xlsx"
DECLINED_FILE="microservices/shared_data/declinedOrders.xlsx"
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

class OrderInfo(BaseModel):
    order: str
    price: float
    name: str
    address: str
    note: Optional[str] = None
    phone: str

# --- File manager functions ---
def read_orders():
    if os.path.exists(DATA_PATH):
        return pd.read_excel(DATA_PATH)
    return pd.DataFrame(columns=["order", "price", "name", "address", "note", "phone"])

def save_order(info: OrderInfo):
    df = read_orders()
    df.loc[len(df)] = [
        info.order,
        info.price,
        info.name,
        info.address,
        info.note or "",
        info.phone
    ]
    df.to_excel(DATA_PATH, index=False)

def update_order(index: int, updated: OrderInfo):
    df = read_orders()
    if index < 0 or index >= len(df):
        raise IndexError("Invalid index")
    df.loc[index, ["order", "price", "name", "address", "note", "phone"]] = [
        updated.order,
        updated.price,
        updated.name,
        updated.address,
        updated.note or "",
        updated.phone
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
        df = read_orders()
        if index < 0 or index >= len(df):
            raise IndexError("Invalid index")

        deleted = df.iloc[index]
        now = pd.Timestamp.now()

        declined_row = deleted.copy()
        declined_row["time"] = now.strftime("%H:%M:%S")


        if os.path.exists(DECLINED_FILE):
            declined_df = pd.read_excel(DECLINED_FILE)
        else:
            declined_df = pd.DataFrame(columns=list(deleted.index) + ["time"])

        declined_df = pd.concat([declined_df, pd.DataFrame([declined_row])], ignore_index=True)
        declined_df.to_excel(DECLINED_FILE, index=False)

        df = df.drop(index).reset_index(drop=True)
        df.to_excel(DATA_PATH, index=False)

        return {"message": f"Order {index} declined and saved to history"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
