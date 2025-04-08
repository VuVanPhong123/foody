import pandas as pd
import requests
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from kivymd.app import MDApp
from kivy.clock import Clock

class Ingredients(Screen):
    def __init__(self, **kwargs):
        super(Ingredients, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245/255, 177/255, 67/255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)
        self.ingredients_data = {}
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.notification_label = Label(
            text="",
            font_size=16,
            color=(1, 0, 0, 1),
            size_hint_y=None,
            height=30
        )
        self.layout.add_widget(self.notification_label)

        self.scroll_view = ScrollView(size_hint=(1, 0.6))
        self.ingredient_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.ingredient_list.bind(minimum_height=self.ingredient_list.setter('height'))
        self.scroll_view.add_widget(self.ingredient_list)
        self.layout.add_widget(self.scroll_view)

        self.input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        self.name_input = TextInput(hint_text="Tên nguyên liệu", size_hint_x=0.4)
        self.quantity_input = TextInput(hint_text="Số lượng", size_hint_x=0.2, input_filter="float")
        self.unit_input = TextInput(hint_text="Đơn vị (kg, g, l...)", size_hint_x=0.2)
        self.date_input = TextInput(hint_text="Ngày mua (YYYY-MM-DD)", size_hint_x=0.3)
        self.expiry_input = TextInput(hint_text="Hạn sử dụng (YYYY-MM-DD)", size_hint_x=0.3)

        self.input_layout.add_widget(self.name_input)
        self.input_layout.add_widget(self.quantity_input)
        self.input_layout.add_widget(self.unit_input)
        self.input_layout.add_widget(self.date_input)
        self.input_layout.add_widget(self.expiry_input)
        self.layout.add_widget(self.input_layout)

        self.button_layout = BoxLayout(size_hint_y=None, height=50)
        self.add_button = Button(text="Thêm nguyên liệu", on_press=self.add_ingredient)
        self.button_layout.add_widget(self.add_button)
        self.layout.add_widget(self.button_layout)

        self.add_widget(self.layout)

        self.load_ingredients()

    def show_notification(self, message):
        self.notification_label.text = message
        Clock.schedule_once(lambda dt: self.clear_notification(), 3)  

    def clear_notification(self):
        self.notification_label.text = ""

    def load_ingredients(self):
        try:
            url = "http://localhost:8000/ingredients"  
            resp = requests.get(url)
            if resp.status_code == 200:
                data = resp.json()
                self.ingredients_data = {
                    item["ingredient"]: item for item in data
                }

                self.ingredient_list.clear_widgets()
                for item in data:
                    ing_name = item["ingredient"]
                    quantity = item["quantity"]
                    unit = item["unit"]
                    purchase_date = item["purchase_date"]
                    expiry_date = item["expiry_date"]
                    label_text = f"{ing_name} {quantity} {unit} (mua: {purchase_date} | hạn: {expiry_date})"
                    ingredient_box = BoxLayout(orientation='vertical', size_hint_y=None, height=80, padding=(10, 5))
                    label = Label(text=label_text, size_hint_y=None, height=40)

                    button_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
                    use_input = TextInput(hint_text="Nhập số", size_hint_x=0.3, input_filter="float")

                    use_button = Button(
                        text="Sử dụng",
                        size_hint_x=0.35,
                        on_press=lambda btn, ing=ing_name, inp=use_input: self.use_ingredient(ing, inp)
                    )
                    delete_button = Button(
                        text="Xóa",
                        size_hint_x=0.35,
                        on_press=lambda btn, ing=ing_name: self.delete_ingredient(ing)
                    )

                    button_box.add_widget(use_input)
                    button_box.add_widget(use_button)
                    button_box.add_widget(delete_button)

                    ingredient_box.add_widget(label)
                    ingredient_box.add_widget(button_box)

                    self.ingredient_list.add_widget(ingredient_box)

            else:
                print("Error fetching ingredients:", resp.text)

        except Exception as e:
            print("Exception while loading ingredients:", e)

    def use_ingredient(self, ingredient, input_field):
        try:
            amount_str = input_field.text.strip()
            if not self.is_valid_amount(amount_str, ingredient):
                self.show_notification("Vui lòng nhập số lượng hợp lệ!")
                return

            amount = float(amount_str)

            url = f"http://localhost:8000/ingredients/{ingredient}"
            params = {"used_amount": amount} 
            resp = requests.put(url, params=params)
            if resp.status_code == 200:
                self.show_notification(f"Đã sử dụng {amount} {self.ingredients_data[ingredient]['unit']} {ingredient}")
                self.load_ingredients()
            else:
                self.show_notification("Lỗi từ server: " + resp.text)

        except Exception as e:
            print("Lỗi khi sử dụng nguyên liệu:", e)

    def is_valid_amount(self, amount_str, ingredient):
        try:
            if not (amount_str.isnumeric() or self.is_valid_float(amount_str)):
                return False
            amount = float(amount_str)
            if amount <= 0:
                return False
            current_qty = self.ingredients_data.get(ingredient, {}).get("quantity", 0)
            if amount > current_qty:
                return False

            return True
        except ValueError:
            return False

    def is_valid_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def delete_ingredient(self, ingredient):

        try:
            url = f"http://localhost:8000/ingredients/{ingredient}"
            resp = requests.delete(url)
            if resp.status_code == 200:
                self.show_notification(f"Đã xóa nguyên liệu: {ingredient}")
                self.load_ingredients()
            else:
                print("Error deleting ingredient:", resp.text)
        except Exception as e:
            print("Lỗi khi xóa nguyên liệu:", e)

    def add_ingredient(self, instance):
        name = self.name_input.text.strip()
        quantity = self.quantity_input.text.strip()
        unit = self.unit_input.text.strip()
        date = self.date_input.text.strip()
        expiry = self.expiry_input.text.strip()

        if name and quantity and unit and date and expiry:
            try:
                body = {
                    "name": name,
                    "quantity": float(quantity),
                    "unit": unit,
                    "purchase_date": date,
                    "expiry_date": expiry
                }
                url = "http://localhost:8000/ingredients"
                resp = requests.post(url, json=body)
                if resp.status_code == 200:
                    self.show_notification(f"Đã thêm nguyên liệu: {name}")
                    self.load_ingredients()
                else:
                    print("Error adding ingredient:", resp.text)
            except Exception as e:
                print("Lỗi khi thêm nguyên liệu:", e)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
