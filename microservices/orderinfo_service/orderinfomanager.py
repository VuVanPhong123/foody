import pandas as pd
import os

class OrderInfoManager:
    def __init__(self, filepath='microservices/orderinfo_service/data/orderInfo.xlsx'):
        self.filepath = filepath

    def read_orders(self):
        if os.path.exists(self.filepath):
            try:
                return pd.read_excel(self.filepath)
            except Exception as e:
                print(f"Error reading orders: {e}")
        return pd.DataFrame()

    def update_order(self, index, name, phone, address, note):
        try:
            df = self.read_orders()
            df.at[index, "name"] = name
            df.at[index, "phone"] = phone
            df.at[index, "address"] = address
            df.at[index, "note"] = note
            df.to_excel(self.filepath, index=False)
        except Exception as e:
            print(f"Error updating order: {e}")

    def delete_order(self, index):
        try:
            df = self.read_orders()
            df.drop(index=index, inplace=True)
            df.reset_index(drop=True, inplace=True)
            df.to_excel(self.filepath, index=False)
        except Exception as e:
            print(f"Error deleting order: {e}")
    def save_order_info(self, name, phone, address, note, order, price):
        df = self.read_orders()
        new_order = {
            "name": name,
            "phone": phone,
            "address": address,
            "note": note,
            "order": order,
            "price": price
        }
        df = df._append(new_order, ignore_index=True)
        df.to_excel(self.filepath, index=False)
