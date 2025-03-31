import pandas as pd
from datetime import datetime

class OrderManager:
    def __init__(self, menu_file='data/food.xlsx', revenue_file='data/revenue.xlsx'):
        # Load the menu of items from food.xlsx
        self.menu = self.load_menu(menu_file)
        self.revenue_file = revenue_file

    def load_menu(self, menu_file):
        """
        Load the menu from an Excel file with columns like ['food', 'price'].
        """
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
        """
        Increase the quantity of `item` in the `selected_items` dict by `quantity`.
        Only applies if `item` exists in self.menu.
        """
        if item in self.menu:
            if quantity > 0:
                selected_items[item] = selected_items.get(item, 0) + quantity
        else:
            print(f"Item '{item}' not found in menu.")

    def calculate_total(self, selected_items):
        """
        Given a dict of {food_item: quantity}, return the total price based on self.menu.
        """
        total = 0
        for item, qty in selected_items.items():
            price_per_item = self.menu.get(item, 0)
            total += price_per_item * qty
        return total

    def save_order(self, selected_items):
        """
        Original method: expects a dict of {food_item: quantity}.
        It calculates total price, builds a 'done_orders' string, and then appends to revenue.xlsx.
        """
        total_price = self.calculate_total(selected_items)
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M')

        # Build 'done_orders' string like "Burger x1, Fries x2"
        done_orders_list = [f"{item} x{qty}" for item, qty in selected_items.items() if qty > 0]
        if not done_orders_list:
            print("No items in this order, skipping save.")
            return
        done_orders_str = ", ".join(done_orders_list)

        # Append to revenue
        self._append_to_revenue(date_str, time_str, done_orders_str, total_price)

    # -------------------------------------------------------------------
    # New method that directly takes a "done_orders_str" plus "total_price"
    # for situations where you already built that string in the UI.
    # -------------------------------------------------------------------
    def save_order_v2(self, done_orders_str, total_price):
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M')

        # If the string is empty or just whitespace, skip
        if not done_orders_str.strip():
            print("No items in done_orders_str, skipping save.")
            return

        # Append to revenue
        self._append_to_revenue(date_str, time_str, done_orders_str, total_price)

    def _append_to_revenue(self, date_str, time_str, done_orders_str, total_price):
        """
        Internal helper to unify writing a single new row into the Excel file.
        """
        new_row = {
            "date": [date_str],
            "time": [time_str],
            "done_orders": [done_orders_str],
            "price": [total_price]
        }
        df_new = pd.DataFrame(new_row)

        # Try to read existing revenue, then append
        try:
            df_existing = pd.read_excel(self.revenue_file)
            df_out = pd.concat([df_existing, df_new], ignore_index=True)
        except FileNotFoundError:
            # If revenue file doesn't exist yet, start fresh
            df_out = df_new
        except Exception as e:
            print(f"Error reading revenue file: {e}")
            return

        # Write the updated DataFrame back to revenue.xlsx
        try:
            df_out.to_excel(self.revenue_file, index=False)
            print("Order appended to revenue file successfully!")
        except Exception as e:
            print(f"Error saving revenue file: {e}")
