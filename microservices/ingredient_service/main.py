from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from ingredientmanager import IngredientManager
import uvicorn
app = FastAPI(title="Ingredient Service")
manager = IngredientManager()  # This now loads data/ingredients.xlsx by default

class IngredientIn(BaseModel):
    name: str
    quantity: float
    unit: str
    purchase_date: str
    expiry_date: str

@app.get("/ingredients")
def list_ingredients():
    # Return a list of existing ingredients
    results = []
    for ing_name, info in manager.ingredients.items():
        results.append({
            "ingredient": ing_name,
            "quantity": info["quantity"],
            "unit": info["unit"],
            "purchase_date": str(info["purchase_date"]),
            "expiry_date": str(info["expiry_date"]),
        })
    return results

@app.post("/ingredients")
def add_ingredient(item: IngredientIn):
    # Add a new ingredient
    manager.add_ingredient(
        name=item.name,
        quantity=item.quantity,
        unit=item.unit,
        purchase_date=item.purchase_date,
        expiry_date=item.expiry_date
    )
    return {"message": f"Ingredient '{item.name}' added"}

@app.put("/ingredients/{name}")
def use_ingredient(name: str, used_amount: float):
    if name not in manager.ingredients:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    if used_amount <= 0:
        raise HTTPException(status_code=400, detail="Used amount must be positive")
    manager.update_ingredient(name, used_amount)  # subtract used_amount
    return {"message": f"Used {used_amount} of '{name}'"}

@app.delete("/ingredients/{name}")
def delete_ingredient(name: str):
    if name not in manager.ingredients:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    manager.delete_ingredient(name)
    return {"message": f"Ingredient '{name}' deleted"}
if __name__ == "__main__":
    # Ingredient Service runs on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)