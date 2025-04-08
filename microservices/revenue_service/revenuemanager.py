import pandas as pd

class RevenueManager:
    def __init__(self, revenue_file='microservices/shared_data/revenue.xlsx'):
        self.revenue_file = revenue_file

    def load_revenue_data(self):
        try:
            df = pd.read_excel(self.revenue_file)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            return df
        except Exception as e:
            print(f"Error loading revenue data: {e}")
            return pd.DataFrame()

    def get_revenue_for_day(self):
        df = self.load_revenue_data().copy()
        if df.empty:
            return df
        today = pd.Timestamp('now').normalize()
        mask = (df['date'].dt.normalize() == today)
        return df.loc[mask]

    def get_revenue_for_week(self):
        df = self.load_revenue_data().copy()
        if df.empty:
            return df
        today = pd.Timestamp('now').normalize()
        start_of_week = today - pd.Timedelta(days=today.weekday())
        mask = (df['date'].dt.normalize() >= start_of_week)
        return df.loc[mask]

    def get_revenue_for_month(self):
        df = self.load_revenue_data().copy()
        if df.empty:
            return df
        now = pd.Timestamp('now')
        mask = (
            (df['date'].dt.year == now.year) &
            (df['date'].dt.month == now.month)
        )
        return df.loc[mask]

    def get_total_revenue(self):
        df = self.load_revenue_data().copy()
        return df
