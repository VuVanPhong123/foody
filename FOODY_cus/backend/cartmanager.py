import pandas as pd
import os

class CartManager:
    def __init__(self, cart_file='data/cart.xlsx'):
        self.cart_file = cart_file
    def read_cart(self):
        try:
            df = pd.read_excel(self.cart_file)
            return df
        except Exception as e:
            print(f"Error reading cart: {e}")
            return pd.DataFrame()

    def write_cart(self, selected_quantities, menu_items):
        prices = {item['name']: item['price'] for item in menu_items}

        # Build the combined string
        order_list = [f"{name} x{qty}" for name, qty in selected_quantities.items() if qty > 0]
        total_price = sum(prices[name] * qty for name, qty in selected_quantities.items() if qty > 0)

        if not order_list:
            print("No items selected — cart not saved.")
            return

        order_str = ", ".join(order_list)

        try:
            df_new = pd.DataFrame([{"order": order_str, "price": total_price}])

            if os.path.exists(self.cart_file):
                df_existing = pd.read_excel(self.cart_file)
                df_out = pd.concat([df_existing, df_new], ignore_index=True)
            else:
                df_out = df_new

            df_out.to_excel(self.cart_file, index=False)
            print("Cart saved")

        except Exception as e:
            print(f"Failed to save cart: {e}")
    def clear_cart(self):
        try:
            pd.DataFrame(columns=["order", "price"]).to_excel(self.cart_file, index=False)
        except Exception as e:
            print(f"Failed to clear cart: {e}")

    def delete_order(self, order, price):
        try:
            df = self.read_cart()
            df = df[~((df['order'] == order) & (df['price'] == price))]
            df.to_excel(self.cart_file, index=False)
        except Exception as e:
            print(f"Error deleting order: {e}")
