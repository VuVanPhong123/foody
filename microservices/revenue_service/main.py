from fastapi import FastAPI
from revenuemanager import RevenueManager
import uvicorn
import pandas as pd

app = FastAPI(title="Revenue Service")
manager = RevenueManager()  # loads data/revenue.xlsx by default

@app.get("/revenue/daily")
def get_daily_revenue():
    df = manager.get_revenue_for_day()
    if df.empty:
        return {"rows": [], "total_sum": 0}

    # Convert price to Python int
    df['price'] = df['price'].astype(int)

    rows = []
    for _, row in df.iterrows():
        rows.append({
            "date": str(row["date"].date()) if pd.notna(row["date"]) else "",
            "time": str(row["time"]),
            "done_orders": str(row["done_orders"]),
            "price": int(row["price"])
        })

    total_sum = int(df['price'].sum())
    return {"rows": rows, "total_sum": total_sum}


@app.get("/revenue/weekly")
def get_weekly_revenue():
    df = manager.get_revenue_for_week()
    if df.empty:
        return {"rows": [], "total_sum": 0}

    # Group by day_name, day, month, year
    df['date_only'] = df['date'].dt.normalize()
    df['day'] = df['date_only'].dt.day
    df['month'] = df['date_only'].dt.month
    df['year'] = df['date_only'].dt.year
    df['day_name_en'] = df['date_only'].dt.day_name()

    en2vi = {
        "Monday": "Thứ 2",
        "Tuesday": "Thứ 3",
        "Wednesday": "Thứ 4",
        "Thursday": "Thứ 5",
        "Friday": "Thứ 6",
        "Saturday": "Thứ 7",
        "Sunday": "Chủ Nhật"
    }
    df['day_name_vi'] = df['day_name_en'].map(en2vi)

    grouped = df.groupby(['date_only','day','month','year','day_name_vi'])['price'].sum().reset_index()
    grouped["price"] = grouped["price"].astype(int)

    rows = []
    for _, row_g in grouped.iterrows():
        rows.append({
            "day_name_vi": row_g["day_name_vi"],
            "day": int(row_g["day"]),
            "month": int(row_g["month"]),
            "year": int(row_g["year"]),
            "price": int(row_g["price"]),
        })

    total_sum = int(grouped["price"].sum())
    return {"rows": rows, "total_sum": total_sum}


@app.get("/revenue/monthly")
def get_monthly_revenue():
    df = manager.get_revenue_for_month()
    if df.empty:
        return {"rows": [], "total_sum": 0}

    df['date_only'] = df['date'].dt.normalize()
    df['day'] = df['date_only'].dt.day
    df['month'] = df['date_only'].dt.month
    df['year'] = df['date_only'].dt.year

    grouped = df.groupby(['year','month','day'])['price'].sum().reset_index()
    grouped["price"] = grouped["price"].astype(int)

    rows = []
    for _, row_g in grouped.iterrows():
        rows.append({
            "day": int(row_g["day"]),
            "month": int(row_g["month"]),
            "year": int(row_g["year"]),
            "price": int(row_g["price"])
        })

    total_sum = int(grouped["price"].sum())
    return {"rows": rows, "total_sum": total_sum}


@app.get("/revenue/total")
def get_total_revenue():
    df = manager.get_total_revenue()
    if df.empty:
        return {"rows": [], "total_sum": 0}

    df['year_month'] = df['date'].dt.strftime('%Y-%m')

    grouped = df.groupby('year_month')['price'].sum().reset_index()
    grouped["price"] = grouped["price"].astype(int)

    rows = []
    for _, row_g in grouped.iterrows():
        rows.append({
            "year_month": row_g["year_month"],
            "price": int(row_g["price"])
        })

    total_sum = int(grouped["price"].sum())
    return {"rows": rows, "total_sum": total_sum}


if __name__ == "__main__":
    # Start the service on port 8002 (customize if you like)
    uvicorn.run(app, host="0.0.0.0", port=8002)
