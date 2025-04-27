from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import os
import uvicorn
import requests

app = FastAPI(title="Online Order Service")

ORDER_FILE    = "microservices/shared_data/orderInfo.xlsx"
DECLINED_FILE = "microservices/shared_data/declinedOrders.xlsx"
DONE_FILE     = "microservices/shared_data/doneOrders.xlsx"

REVENUE_URL   = "http://localhost:8002/revenue"

os.makedirs(os.path.dirname(ORDER_FILE   ), exist_ok=True)
os.makedirs(os.path.dirname(DECLINED_FILE), exist_ok=True)
os.makedirs(os.path.dirname(DONE_FILE    ), exist_ok=True)

class Order(BaseModel):
    name: str
    phone: str
    address: str
    note: Optional[str] = None
    order: str
    price: float
def _append_row(path: str, row: dict):
    """Append a dict as a new row to an Excel file (create if missing)."""
    if os.path.exists(path) and os.path.getsize(path) > 0:
        df = pd.read_excel(path, engine="openpyxl")
    else:
        df = pd.DataFrame(columns=row.keys())
    df.loc[len(df)] = row
    df.to_excel(path, index=False, engine="openpyxl")

@app.get("/onlineorders")
def list_orders():
    if not os.path.exists(ORDER_FILE) or os.path.getsize(ORDER_FILE) == 0:
        return []
    try:
        df = pd.read_excel(ORDER_FILE, engine="openpyxl")
    except Exception:
        return []
    return df.to_dict(orient="records")

@app.delete("/onlineorders/{idx}")
def decline_order(idx: int):
    try:
        df = pd.read_excel(ORDER_FILE, engine="openpyxl")
        if idx < 0 or idx >= len(df):
            raise IndexError("Invalid index")

        row = df.iloc[idx]
        now = pd.Timestamp.now()
        declined = row.copy()
        declined["time"] = now.strftime("%H:%M:%S")
        declined["date"] = now.strftime("%Y-%m-%d")

        _append_row(DECLINED_FILE, declined.to_dict())
        df.drop(index=idx).reset_index(drop=True) \
          .to_excel(ORDER_FILE, index=False, engine="openpyxl")
        return {"message": "Order declined"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/onlineorders/{idx}")
def complete_order(idx: int):
    try:
        df = pd.read_excel(ORDER_FILE, engine="openpyxl")
        if idx < 0 or idx >= len(df):
            raise IndexError("Invalid index")

        order = df.loc[idx]
        now   = pd.Timestamp.now()
        payload = {
            "done_orders": str(order["order"]),
            "price"      : float(order["price"]),
            "time"       : now.strftime("%H:%M:%S"),
            "date"       : now.strftime("%Y-%m-%d")
        }

        r = requests.post(REVENUE_URL, json=payload, timeout=5)
        if r.status_code != 200:
            raise RuntimeError(f"Revenue service error: {r.text}")
        _append_row(DONE_FILE, payload)

        df.drop(index=idx).reset_index(drop=True) \
          .to_excel(ORDER_FILE, index=False, engine="openpyxl")
        return {"message": "Order completed & revenue updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006)
