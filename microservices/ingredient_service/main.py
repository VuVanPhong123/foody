from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd, os, uvicorn


EXCEL_PATH = "microservices/ingredient_service/data/ingredients.xlsx"
os.makedirs(os.path.dirname(EXCEL_PATH), exist_ok=True)



class IngredientManager:
    def __init__(self, path: str = EXCEL_PATH):
        self.path = path
        self.ingredients = self._load()


    def _load(self):
        if not os.path.exists(self.path):
            return {}
        try:
            df = pd.read_excel(self.path, engine="openpyxl")
            data = {}
            for _, row in df.iterrows():
                data[row["ingredient"]] = {
                    "quantity": float(row["quantity"]),
                    "unit": row["unit"],
                    "purchase_date": row["purchase_date"],
                    "expiry_date": row["expiry_date"],
                }
            return data
        except Exception as e:
            print("Error loading ingredients:", e)
            return {}

    def _save(self):
        rows = [
            {
                "ingredient": k,
                "quantity": v["quantity"],
                "unit": v["unit"],
                "purchase_date": v["purchase_date"],
                "expiry_date": v["expiry_date"],
            }
            for k, v in self.ingredients.items()
        ]
        df = pd.DataFrame(rows)
        df.to_excel(self.path, index=False, engine="openpyxl")
    def add(self, *, name, quantity, unit, purchase_date, expiry_date):
        if name in self.ingredients:
            # merge quantities if same ingredient is re-added
            self.ingredients[name]["quantity"] += quantity
        else:
            self.ingredients[name] = {
                "quantity": quantity,
                "unit": unit,
                "purchase_date": purchase_date,
                "expiry_date": expiry_date,
            }
        self._save()

    def use(self, name, used_amount):
        if name not in self.ingredients:
            raise KeyError("ingredient missing")
        if used_amount <= 0:
            raise ValueError("amount must be > 0")
        self.ingredients[name]["quantity"] = max(
            0, self.ingredients[name]["quantity"] - used_amount
        )
        self._save()

    def delete(self, name):
        if name in self.ingredients:
            del self.ingredients[name]
            self._save()

app = FastAPI(title="Ingredient Service")

manager = IngredientManager()


class IngredientIn(BaseModel):
    name: str
    quantity: float
    unit: str
    purchase_date: str
    expiry_date: str


@app.get("/ingredients")
def list_ingredients():
    return [
        {
            "ingredient": k,
            **v,
        }
        for k, v in manager.ingredients.items()
    ]


@app.post("/ingredients")
def add_ingredient(item: IngredientIn):
    manager.add(
        name=item.name,
        quantity=item.quantity,
        unit=item.unit,
        purchase_date=item.purchase_date,
        expiry_date=item.expiry_date,
    )
    return {"message": f"Ingredient '{item.name}' added"}


@app.put("/ingredients/{name}")
def use_ingredient(name: str, used_amount: float):
    try:
        manager.use(name, used_amount)
        return {"message": f"Used {used_amount} of '{name}'"}
    except KeyError:
        raise HTTPException(404, "Ingredient not found")
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.delete("/ingredients/{name}")
def delete_ingredient(name: str):
    if name not in manager.ingredients:
        raise HTTPException(404, "Ingredient not found")
    manager.delete(name)
    return {"message": f"Ingredient '{name}' deleted"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
