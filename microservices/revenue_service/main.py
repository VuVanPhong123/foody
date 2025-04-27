
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date, timedelta
import sqlite3
import pandas as pd
import os
import uvicorn


DB_PATH       = "microservices/shared_data/revenue.db"
EXCEL_EXPORT  = "microservices/shared_data/revenue.xlsx"   

os.makedirs(os.path.dirname(DB_PATH),      exist_ok=True)
os.makedirs(os.path.dirname(EXCEL_EXPORT), exist_ok=True)

class RevenueManager:

    def __init__(self, db_path: str = DB_PATH):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS revenue ("
            " id           INTEGER PRIMARY KEY AUTOINCREMENT,"
            " done_orders  TEXT,"
            " price        INTEGER,"
            " time         TEXT,"
            " date         TEXT)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_revenue_date ON revenue(date)"
        )
        self.conn.commit()

        if self._is_empty() and os.path.exists(EXCEL_EXPORT):
            try:
                legacy = pd.read_excel(EXCEL_EXPORT)
                for _, r in legacy.iterrows():
                    self.add_row(
                        r["done_orders"],
                        int(r["price"]),
                        str(r["time"]),
                        str(pd.to_datetime(r["date"]).date())
                    )
                print(f"[Revenue] Imported {len(legacy)} rows from revenue.xlsx")
            except Exception as e:
                print("[Revenue] Could not import legacy Excel:", e)

    def _is_empty(self) -> bool:
        cur = self.conn.execute("SELECT 1 FROM revenue LIMIT 1")
        return cur.fetchone() is None

    def _query(self, where: str = "", params: tuple = ()) -> pd.DataFrame:
        sql = "SELECT done_orders, price, time, date FROM revenue"
        if where:
            sql += f" WHERE {where}"
        return pd.read_sql(sql, self.conn, params=params, parse_dates=["date"])

    def add_row(self, done_orders: str, price: int, time: str, date_: str) -> None:
        self.conn.execute(
            "INSERT INTO revenue(done_orders,price,time,date) VALUES(?,?,?,?)",
            (done_orders, price, time, date_),
        )
        self.conn.commit()

    def get_revenue_for_day(self) -> pd.DataFrame:
        return self._query("date(date)=date(?)", (date.today(),))

    def get_revenue_for_week(self) -> pd.DataFrame:
        start = date.today() - timedelta(days=date.today().weekday())  # Monday
        return self._query("date(date)>=date(?)", (start,))

    def get_revenue_for_month(self) -> pd.DataFrame:
        ym = date.today().strftime("%Y-%m")
        return self._query("strftime('%Y-%m',date)=?", (ym,))

    def get_total_revenue(self) -> pd.DataFrame:
        return self._query()

app     = FastAPI(title="Revenue Service (single-file)")
manager = RevenueManager()

class RevenueEntry(BaseModel):
    done_orders: str
    price: float
    time: str
    date: str   

@app.post("/revenue")
def add_revenue(entry: RevenueEntry):
    try:
        manager.add_row(
            done_orders=entry.done_orders,
            price=int(entry.price),
            time=entry.time,
            date_=entry.date
        )
        manager.get_total_revenue().to_excel(EXCEL_EXPORT, index=False)
        return {"message": "Revenue entry added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/revenue/daily")
def get_daily_revenue():
    df = manager.get_revenue_for_day()
    if df.empty:
        return {"rows": [], "total_sum": 0}

    df["price"] = df["price"].astype(int)
    df["date"]  = df["date"].dt.date
    return {"rows": df.to_dict("records"),
            "total_sum": int(df["price"].sum())}


@app.get("/revenue/weekly")
def get_weekly_revenue():
    df = manager.get_revenue_for_week()
    if df.empty:
        return {"rows": [], "total_sum": 0}

    g = (
        df.assign(date_only=df["date"].dt.normalize())
          .groupby("date_only")["price"].sum()
          .reset_index()
    )
    g["day_name_vi"] = g["date_only"].dt.day_name().map({
        "Monday": "Thứ 2", "Tuesday": "Thứ 3", "Wednesday": "Thứ 4",
        "Thursday": "Thứ 5", "Friday": "Thứ 6", "Saturday": "Thứ 7",
        "Sunday": "Chủ Nhật"
    })
    g["day"]   = g["date_only"].dt.day
    g["month"] = g["date_only"].dt.month
    g["year"]  = g["date_only"].dt.year
    g["price"] = g["price"].astype(int)

    return {"rows": g[["day_name_vi","day","month","year","price"]].to_dict("records"),
            "total_sum": int(g["price"].sum())}


@app.get("/revenue/monthly")
def get_monthly_revenue():
    df = manager.get_revenue_for_month()
    if df.empty:
        return {"rows": [], "total_sum": 0}

    g = (
        df.assign(date_only=df["date"].dt.normalize())
          .groupby("date_only")["price"].sum()
          .reset_index()
    )
    g["day"]   = g["date_only"].dt.day
    g["month"] = g["date_only"].dt.month
    g["year"]  = g["date_only"].dt.year
    g["price"] = g["price"].astype(int)

    return {"rows": g[["day","month","year","price"]].to_dict("records"),
            "total_sum": int(g["price"].sum())}


@app.get("/revenue/total")
def get_total_revenue():
    df = manager.get_total_revenue()
    if df.empty:
        return {"rows": [], "total_sum": 0}

    df["year_month"] = df["date"].dt.strftime("%Y-%m")
    g = df.groupby("year_month")["price"].sum().astype(int).reset_index()

    return {"rows": g.to_dict("records"),
            "total_sum": int(g["price"].sum())}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
