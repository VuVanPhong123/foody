import pandas as pd

class IngredientManager:
    def __init__(self, ingredient_file='microservices/ingredient_service/data/ingredients.xlsx'):
        
        self.ingredients_file = ingredient_file
        self.ingredients = self.load_ingredients(ingredient_file)

    def load_ingredients(self, ingredient_file):
        ingredients = {}
        try:
            df = pd.read_excel(ingredient_file)
            for _, row in df.iterrows():
                ingredient = row['ingredient']
                quantity = row['quantity']
                ingredients[ingredient] = {
                    'quantity': float(quantity),  
                    'unit': row['unit'],
                    'purchase_date': row['purchase_date'],
                    'expiry_date': row['expiry_date']
                }
        except Exception as e:
            print("Error loading ingredients:", e)
        return ingredients

    def save_ingredients(self):
        data = []
        for ingredient, info in self.ingredients.items():
            data.append({
                'ingredient': ingredient,
                'quantity': info['quantity'],
                'unit': info['unit'],
                'purchase_date': info['purchase_date'],
                'expiry_date': info['expiry_date']
            })
        df = pd.DataFrame(data)
        df.to_excel(self.ingredients_file, index=False)

    def add_ingredient(self, name, quantity, unit, purchase_date, expiry_date):
        
        try:
            df = pd.read_excel(self.ingredients_file)

            new_ingredient = {
                'ingredient': name,
                'quantity': quantity,
                'unit': unit,
                'purchase_date': purchase_date,
                'expiry_date': expiry_date
            }
            new_ingredient_df = pd.DataFrame([new_ingredient])
            new_ingredient_df = new_ingredient_df.dropna(axis='columns', how='all')
            df = pd.concat([df, new_ingredient_df], ignore_index=True, join='outer', sort=False)
            df.to_excel(self.ingredients_file, index=False)
            self.ingredients = self.load_ingredients(self.ingredients_file)
        except Exception as e:
            print(f"Error adding ingredient: {e}")

    def update_ingredient(self, ingredient, quantity_used):
        if ingredient in self.ingredients:
            self.ingredients[ingredient]['quantity'] -= quantity_used
            if self.ingredients[ingredient]['quantity'] < 0:
                self.ingredients[ingredient]['quantity'] = 0

            self.save_ingredients()
        else:
            print(f"Ingredient {ingredient} not found in inventory.")

    def delete_ingredient(self, ingredient):
        try:
            df = pd.read_excel(self.ingredients_file)
            df = df[df['ingredient'] != ingredient]
            df.to_excel(self.ingredients_file, index=False)
            self.ingredients = self.load_ingredients(self.ingredients_file)
        except Exception as e:
            print(f"Error deleting ingredient: {e}")

    def get_unit(self, ingredient):
        try:
            df = pd.read_excel(self.ingredients_file)
            row = df.loc[df['ingredient'] == ingredient]
            if not row.empty:
                return row['unit'].values[0]
        except Exception as e:
            print(f"Error retrieving unit for {ingredient}: {e}")
        return ""

    def get_purchase_date(self, ingredient):
        try:
            df = pd.read_excel(self.ingredients_file)
            row = df.loc[df['ingredient'] == ingredient]
            if not row.empty:
                return row['purchase_date'].values[0]
        except Exception as e:
            print(f"Error retrieving purchase date for {ingredient}: {e}")
        return ""

    def get_expiry_date(self, ingredient):
        try:
            df = pd.read_excel(self.ingredients_file)
            row = df.loc[df['ingredient'] == ingredient]
            if not row.empty:
                return row['expiry_date'].values[0]
        except Exception as e:
            print(f"Error retrieving expiry date for {ingredient}: {e}")
        return ""
