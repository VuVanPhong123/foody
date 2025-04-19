

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import os
import uvicorn

app = FastAPI(title="Online Order Service")

ORDER_FILE = "microservices/shared_data/orderInfo.xlsx"
DECLINED_FILE = "microservices/shared_data/declinedOrders.xlsx"
DONE_FILE = "microservices/shared_data/doneOrders.xlsx"
REVENUE_FILE = "microservices/shared_data/revenue.xlsx"

os.makedirs(os.path.dirname(ORDER_FILE), exist_ok=True)
os.makedirs(os.path.dirname(REVENUE_FILE), exist_ok=True)

class Order(BaseModel):
    name: str
    phone: str
    address: str
    note: Optional[str] = None
    order: str
    price: float

@app.get("/onlineorders")
def get_online_orders():
    if not os.path.exists(ORDER_FILE):
        return []
    try:
        df = pd.read_excel(ORDER_FILE)
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

@app.delete("/onlineorders/{index}")
def delete_order(index: int):
    try:
        df = pd.read_excel(ORDER_FILE)
        if index < 0 or index >= len(df):
            raise IndexError("Invalid index")
        deleted = df.iloc[index]
        now = pd.Timestamp.now()

        declined_row = deleted.copy()
        declined_row["time"] = now.strftime("%H:%M:%S")
        declined_row["date"] = now.strftime("%Y-%m-%d")

        if os.path.exists(DECLINED_FILE):
            declined_df = pd.read_excel(DECLINED_FILE)
        else:
            declined_df = pd.DataFrame(columns=list(deleted.index) + ["time", "date"])

        declined_df = pd.concat([declined_df, pd.DataFrame([declined_row])], ignore_index=True)
        declined_df.to_excel(DECLINED_FILE, index=False)

        df = df.drop(index).reset_index(drop=True)
        df.to_excel(ORDER_FILE, index=False)

        return {"message": "Order declined and moved to declinedOrders.xlsx"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/onlineorders/{index}")
def mark_order_completed(index: int):
    try:
        df = pd.read_excel(ORDER_FILE)
        if index < 0 or index >= len(df):
            raise IndexError("Invalid index")

        order = df.loc[index]
        now = pd.Timestamp.now()

        new_row = {
            "done_orders": order["order"],
            "price": order["price"],
            "time": now.strftime("%H:%M:%S"),
            "date": now.strftime("%Y-%m-%d")
        }

        if os.path.exists(REVENUE_FILE):
            revenue_df = pd.read_excel(REVENUE_FILE)
        else:
            revenue_df = pd.DataFrame(columns=["done_orders", "price", "time", "date"])
        revenue_df.loc[len(revenue_df)] = new_row
        revenue_df.to_excel(REVENUE_FILE, index=False)

        if os.path.exists(DONE_FILE):
            done_df = pd.read_excel(DONE_FILE)
        else:
            done_df = pd.DataFrame(columns=["done_orders", "price", "time", "date"])
        done_df.loc[len(done_df)] = new_row
        done_df.to_excel(DONE_FILE, index=False)

        df = df.drop(index).reset_index(drop=True)
        df.to_excel(ORDER_FILE, index=False)

        return {"message": "Order marked complete and saved to revenue and doneOrders.xlsx"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006)

