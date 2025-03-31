import pandas as pd

class RevenueManager:
    def __init__(self, revenue_file='data/revenue.xlsx'):
        self.revenue_file = revenue_file
        self.revenue_data = self.load_revenue_data()

    def load_revenue_data(self):
        try:
            df = pd.read_excel(self.revenue_file)
 
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            return df
        except Exception as e:
            print(f"Error loading revenue data: {e}")
            return pd.DataFrame()

    def get_revenue_by_period(self, period):
        if period == 'day':
            return self.get_revenue_for_day()
        elif period == 'week':
            return self.get_revenue_for_week()
        elif period == 'month':
            return self.get_revenue_for_month()
        else:
            return self.get_total_revenue()

    def get_revenue_for_day(self):
        # 'date' must be datetime
        today = pd.Timestamp('now').normalize()
        mask = (self.revenue_data['date'].dt.normalize() == today)
        return self.revenue_data.loc[mask]

    def get_revenue_for_week(self):
        today = pd.Timestamp('now').normalize()
        start_of_week = today - pd.Timedelta(days=today.weekday())
        mask = (self.revenue_data['date'].dt.normalize() >= start_of_week)
        return self.revenue_data.loc[mask]

    def get_revenue_for_month(self):
        now = pd.Timestamp('now')
        mask = (
            (self.revenue_data['date'].dt.year == now.year) &
            (self.revenue_data['date'].dt.month == now.month)
        )
        return self.revenue_data.loc[mask]

    def get_total_revenue(self):
        return self.revenue_data

    def parse_done_orders(self, done_orders_str):
        orders = done_orders_str.split(',')
        orders_dict = {}
        for order in orders:
            item, qty = order.strip().split(' x')
            orders_dict[item] = int(qty)
        return orders_dict
