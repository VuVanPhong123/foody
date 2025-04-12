from fastapi import FastAPI
import pandas as pd
import os
import uvicorn

app = FastAPI(title="Order History Service")

DONE_PATH = "microservices/shared_data/doneOrders.xlsx"
DECLINED_PATH = "microservices/shared_data/declinedOrders.xlsx"

@app.get("/history")
def get_order_history():
    history = []

    if os.path.exists(DONE_PATH):
        done_df = pd.read_excel(DONE_PATH)
        for _, row in done_df.iterrows():
            history.append({
                "order": str(row.get("done_orders", "")).replace(",", "\n"),
                "price": row.get("price", 0),
                "time": str(row.get("time", "--")),
                "date": str(row.get("date", "--")),
                "status": "Đã hoàn thành"
            })

    if os.path.exists(DECLINED_PATH):
        declined_df = pd.read_excel(DECLINED_PATH)
        for _, row in declined_df.iterrows():
            history.append({
                "order": str(row.get("order", "")).replace(",", "\n"),
                "price": row.get("price", 0),
                "time": str(row.get("time", "--")),
                "date": str(row.get("date", "--")),
                "status": "Đã hủy"
            })

    return sorted(history, key=lambda x: (x['date'], x['time']), reverse=True)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8007)
