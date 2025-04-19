from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
import json
import uvicorn

app = FastAPI(title="Cart Service")
CART_FILE = "microservices/cart_service/data/cart.xlsx"

class CartRequest(BaseModel):
    quantities: dict  
    menu_items: list  

def read_cart_from_excel():
    if not os.path.exists(CART_FILE):
        return pd.DataFrame(columns=["item_names", "quantities", "total_price"])

    df = pd.read_excel(CART_FILE)

    def safe_parse_json(x):
        if isinstance(x, str) and x.strip().startswith('['):
            try:
                return json.loads(x)
            except json.JSONDecodeError:
                print(f"Invalid JSON: {x}")
                return []
        return x

    for col in ['item_names', 'quantities']:
        if col in df.columns:
            df[col] = df[col].apply(safe_parse_json)

    return df

def write_cart_to_excel(df):
    for col in ['item_names', 'quantities']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)

    os.makedirs(os.path.dirname(CART_FILE), exist_ok=True)
    df.to_excel(CART_FILE, index=False)

@app.post("/cart")
def save_cart(cart: CartRequest):
    new_items = []
    for item in cart.menu_items:
        name = item["name"]
        if name in cart.quantities and cart.quantities[name] > 0:
            qty = cart.quantities[name]
            total = int(item["price"]) * qty
            new_items.append({
                "name": name,
                "quantity": qty,
                "price": total
            })

    if new_items:
        df_items = pd.DataFrame(new_items)
        new_row = {
            "item_names": df_items["name"].tolist(),
            "quantities": df_items["quantity"].tolist(),
            "total_price": int(df_items["price"].sum())
        }

        existing = read_cart_from_excel()
        updated = pd.concat([existing, pd.DataFrame([new_row])], ignore_index=True)
        write_cart_to_excel(updated)

        return {"message": "Cart saved", "count": len(updated)}
    else:
        return {"message": "No items selected."}

@app.get("/cart")
def get_cart():
    try:
        df = read_cart_from_excel()
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/cart")
async def delete_cart(request: Request):
    body = await request.json() if request.headers.get("content-length") != "0" else None
    df = read_cart_from_excel()

    if df.empty:
        return {"message": "Nothing to delete"}

    if not body:
        df = pd.DataFrame(columns=["item_names", "quantities", "total_price"])
        write_cart_to_excel(df)
        return {"message": "Cart cleared"}

    try:
        target_names = body.get("item_names", [])
        target_quantities = body.get("quantities", [])
        target_price = body.get("total_price")

        match_found = False
        for idx, row in df.iterrows():
            row_names = row['item_names'] if isinstance(row['item_names'], list) else []
            row_quantities = row['quantities'] if isinstance(row['quantities'], list) else []
            row_price = row['total_price']

            if row_names == target_names and row_quantities == target_quantities and row_price == target_price:
                df = df.drop(idx)
                match_found = True
                break

        if match_found:
            df = df.reset_index(drop=True)
            write_cart_to_excel(df)
            return {"message": "Specific cart entry deleted", "remaining": len(df)}
        else:
            raise HTTPException(status_code=404, detail="Matching cart entry not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
