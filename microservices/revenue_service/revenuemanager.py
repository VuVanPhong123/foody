import pandas as pd

class RevenueManager:
    def __init__(self, revenue_file='microservices/shared_data/revenue.xlsx'):
        self.revenue_file = revenue_file

    def load_revenue_data(self):
        """
        Re-read the Excel each time so new rows are detected without restarting.
        """
        try:
            df = pd.read_excel(self.revenue_file)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            return df
        except Exception as e:
            print(f"Error loading revenue data: {e}")
            return pd.DataFrame()

    def get_revenue_for_day(self):
        """
        Return today's rows.
        """
        df = self.load_revenue_data().copy()
        if df.empty:
            return df
        today = pd.Timestamp('now').normalize()
        mask = (df['date'].dt.normalize() == today)
        return df.loc[mask]

    def get_revenue_for_week(self):
        """
        Return rows from the current week.
        """
        df = self.load_revenue_data().copy()
        if df.empty:
            return df
        today = pd.Timestamp('now').normalize()
        start_of_week = today - pd.Timedelta(days=today.weekday())
        mask = (df['date'].dt.normalize() >= start_of_week)
        return df.loc[mask]

    def get_revenue_for_month(self):
        """
        Return rows from the current month.
        """
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
        """
        Return all rows.
        """
        df = self.load_revenue_data().copy()
        return df
