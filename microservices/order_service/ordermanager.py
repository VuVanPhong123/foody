import pandas as pd
from datetime import datetime

class OrderManager:
    def __init__(self, menu_file='microservices/order_service/data/food.xlsx', revenue_file='microservices/shared_data/revenue.xlsx'):
        self.menu = self.load_menu(menu_file)
        self.revenue_file = revenue_file

    def load_menu(self, menu_file):
        menu = {}
        try:
            df = pd.read_excel(menu_file)
            for _, row in df.iterrows():
                food_item = row['food']
                price = int(row['price'])
                menu[food_item] = price
        except Exception as e:
            print("Error loading menu:", e)
        return menu

    def add_to_order(self, selected_items, item, quantity):
        if item in self.menu:
            if quantity > 0:
                selected_items[item] = selected_items.get(item, 0) + quantity
        else:
            print(f"Item '{item}' not found in menu.")

    def calculate_total(self, selected_items):
        total = 0
        for item, qty in selected_items.items():
            price_per_item = self.menu.get(item, 0)
            total += price_per_item * qty
        return total

    def save_order(self, selected_items):
        total_price = self.calculate_total(selected_items)
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M')
        done_orders_list = [f"{item} x{qty}" for item, qty in selected_items.items() if qty > 0]
        if not done_orders_list:
            print("No items in this order, skipping save.")
            return
        done_orders_str = ", ".join(done_orders_list)

        # Append to revenue
        self._append_to_revenue(date_str, time_str, done_orders_str, total_price)

    def save_order_v2(self, done_orders_str, total_price):
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M')
        if not done_orders_str.strip():
            print("No items in done_orders_str, skipping save.")
            return

        self._append_to_revenue(date_str, time_str, done_orders_str, total_price)

    def _append_to_revenue(self, date_str, time_str, done_orders_str, total_price):
        new_row = {
            "date": [date_str],
            "time": [time_str],
            "done_orders": [done_orders_str],
            "price": [total_price]
        }
        df_new = pd.DataFrame(new_row)
        try:
            df_existing = pd.read_excel(self.revenue_file)
            df_out = pd.concat([df_existing, df_new], ignore_index=True)
        except FileNotFoundError:
            df_out = df_new
        except Exception as e:
            print(f"Error reading revenue file: {e}")
            return
        try:
            df_out.to_excel(self.revenue_file, index=False)
            print("Order appended to revenue file successfully!")
        except Exception as e:
            print(f"Error saving revenue file: {e}")
