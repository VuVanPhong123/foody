import pandas as pd
import math
import os

class FoodManager:
    def __init__(self, food_file='microservices/food_service/data/food.xlsx', image_folder='microservices/food_service/images'):
        self.food_file = food_file
        self.image_folder = image_folder
        self.menu_items = self.load_menu()

    def load_menu(self):
    
        try:
            df = pd.read_excel(self.food_file)
            if df.empty or not all(col in df.columns for col in ['food', 'price', 'picture']):
                raise ValueError("Excel file must contain 'food', 'price', and 'picture' columns.")

            menu = []
            for idx, row in df.iterrows():
                try:
                    name = str(row['food']).strip()
                    price_str = row['price']
                    image_value = str(row['picture']).strip()

                    if pd.isna(price_str) or not str(price_str).strip().isdigit():
                        print(f"Skipping row {idx} due to invalid price: {price_str}")
                        continue
                    if pd.isna(image_value) or image_value.lower() in ["", "nan"]:
                        print(f"Skipping row {idx} due to missing image path.")
                        continue

                    price = int(price_str)
                    image_path = image_value if os.path.isabs(image_value) or os.path.sep in image_value else os.path.join(self.image_folder, image_value)

                    menu.append({"name": name, "price": price, "image": image_path})
                except Exception as e:
                    print(f"Skipping row {idx} due to error: {e}")
                    continue
            return menu
        except Exception as e:
            print(f"Error loading food menu: {e}")
            return []
