from fastapi import FastAPI
import pandas as pd
import os
import uvicorn

app = FastAPI(title="Food Service")

FOOD_FILE = "microservices/food_service/data/food.xlsx"
IMAGE_FOLDER = "microservices/food_service/images"  

@app.get("/menu")
def get_menu():
    if not os.path.exists(FOOD_FILE):
        return []

    try:
        df = pd.read_excel(FOOD_FILE)
        if df.empty or not all(col in df.columns for col in ['food', 'price', 'picture']):
            return []

        menu = []
        for idx, row in df.iterrows():
            try:
                name = str(row['food']).strip()
                price = row['price']
                picture = str(row['picture']).strip()

                # Validate price
                if pd.isna(price) or not str(price).strip().isdigit():
                    continue
                price = int(price)

                # Validate image
                if pd.isna(picture) or picture.lower() in ["", "nan"]:
                    continue

                # Normalize image path
                if os.path.isabs(picture) or os.path.sep in picture:
                    image_path = picture
                else:
                    image_path = os.path.join(IMAGE_FOLDER, picture)

                menu.append({
                    "name": name,
                    "price": price,
                    "image": image_path
                })
            except Exception as e:
                print(f"Skipping row {idx} due to error: {e}")
                continue

        return menu
    except Exception as e:
        print(f"Failed to load menu: {e}")
        return []

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
