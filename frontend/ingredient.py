import pandas as pd
from backend.ingredientmanager import IngredientManager
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
        self.ingredient_manager = IngredientManager()

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
        Clock.schedule_once(lambda dt: self.clear_notification(), 3)  # Ẩn sau 3 giây

    def clear_notification(self):
        self.notification_label.text = ""

    def load_ingredients(self):
        try:
            ingredients = self.ingredient_manager.ingredients
            self.ingredient_list.clear_widgets()

            for ingredient, info in ingredients.items():
                unit = self.ingredient_manager.get_unit(ingredient)
                purchase_date = self.ingredient_manager.get_purchase_date(ingredient)
                expiry_date = self.ingredient_manager.get_expiry_date(ingredient)

                quantity = round(info['quantity'], 2)

                ingredient_box = BoxLayout(orientation='vertical', size_hint_y=None, height=80, padding=(10, 5))

                label_text = f"{ingredient} {quantity} {unit} (mua: {purchase_date} | hạn: {expiry_date})"
                label = Label(text=label_text, size_hint_y=None, height=40)

                button_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
                use_input = TextInput(hint_text="Nhập số", size_hint_x=0.3, input_filter="float")
                use_button = Button(text="Sử dụng", size_hint_x=0.35, on_press=lambda btn, ingredient=ingredient, input=use_input: self.use_ingredient(ingredient, input))
                delete_button = Button(text="Xóa", size_hint_x=0.35, on_press=lambda btn, ingredient=ingredient: self.delete_ingredient(ingredient))

                button_box.add_widget(use_input)
                button_box.add_widget(use_button)
                button_box.add_widget(delete_button)

                ingredient_box.add_widget(label)
                ingredient_box.add_widget(button_box)

                self.ingredient_list.add_widget(ingredient_box)
        except Exception as e:
            print("Lỗi khi đọc file Excel:", e)



    def use_ingredient(self, ingredient, input_field):
        try:

            amount = input_field.text.strip()

            if not self.is_valid_amount(amount, ingredient):
                self.show_notification("Vui lòng nhập số lượng hợp lệ!")
                return
        
            amount = float(amount)
            unit = self.ingredient_manager.get_unit(ingredient)       
            amount = round(amount, 2)
            self.ingredient_manager.update_ingredient(ingredient, amount)
            
            self.show_notification(f"Đã sử dụng {amount} {unit} {ingredient}")
            
            self.load_ingredients()
        except Exception as e:
            print("Lỗi khi sử dụng nguyên liệu:", e)



    def is_valid_amount(self, amount, ingredient):
        try:
            if not (amount.isnumeric() or self.is_valid_float(amount)):
                return False
            amount = float(amount)
            if amount <= 0 or amount > self.ingredient_manager.ingredients.get(ingredient, {'quantity': 0})['quantity']:
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
            self.ingredient_manager.delete_ingredient(ingredient)
            self.show_notification(f"Đã xóa nguyên liệu: {ingredient}")
            self.load_ingredients()
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
                self.ingredient_manager.add_ingredient(name, float(quantity), unit, date, expiry)
                self.show_notification(f"Đã thêm nguyên liệu: {name}")
                self.load_ingredients()  
            except Exception as e:
                print("Lỗi khi thêm nguyên liệu:", e)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
