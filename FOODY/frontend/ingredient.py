# frontend/ingredient.py
import requests, pandas as pd, threading
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivymd.uix.spinner import MDSpinner
from kivymd.app import MDApp

from frontend.roundButton import RoundedButton


class Ingredients(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.ingredients_data = {}
        self.spinner = None 

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.notification_label = Label(text="", font_size=16,
                                        color=(1, 0, 0, 1),
                                        size_hint_y=None, height=30)
        self.layout.add_widget(self.notification_label)

        self.scroll_view = ScrollView(size_hint=(1, .6))
        self.ingredient_list = BoxLayout(orientation='vertical',
                                         size_hint_y=None)
        self.ingredient_list.bind(minimum_height=self.ingredient_list.setter('height'))
        self.scroll_view.add_widget(self.ingredient_list)
        self.layout.add_widget(self.scroll_view)

        self.input_layout = BoxLayout(size_hint_y=None, height=50)
        self.name_input     = TextInput(hint_text="Tên nguyên liệu",  size_hint_x=.4)
        self.quantity_input = TextInput(hint_text="Số lượng",         size_hint_x=.2,
                                        input_filter="float")
        self.unit_input     = TextInput(hint_text="Đơn vị",           size_hint_x=.2)
        self.date_input     = TextInput(hint_text="Ngày mua YYYY-MM-DD",
                                        size_hint_x=.3)
        self.expiry_input   = TextInput(hint_text="Hạn dùng YYYY-MM-DD",
                                        size_hint_x=.3)
        for w in (self.name_input, self.quantity_input, self.unit_input,
                  self.date_input, self.expiry_input):
            self.input_layout.add_widget(w)
        self.layout.add_widget(self.input_layout)

        self.button_layout = BoxLayout(size_hint_y=None, height=50)
        self.add_button = RoundedButton(text="Thêm nguyên liệu",
                                        on_press=self.add_ingredient)
        self.add_button.change_color(233/255,150/255,14/255,1)
        self.add_button.color = (0, 0, 0, 1)
        self.button_layout.add_widget(self.add_button)
        self.layout.add_widget(self.button_layout)

        self.add_widget(self.layout)
        self.load_ingredients()

    def show_spinner(self):
        if self.spinner is None:
            self.spinner = MDSpinner(size_hint=(None, None), size=(46, 46),
                                     line_width=3, color=(1, 1, 1, 1),
                                     pos_hint={'center_x': .5, 'y': 0})
            self.layout.add_widget(self.spinner)

    def hide_spinner(self):
        if self.spinner:
            self.layout.remove_widget(self.spinner)
            self.spinner = None

    def show_notification(self, msg):
        self.notification_label.text = msg
        Clock.schedule_once(lambda dt: self.clear_notification(), 3)

    def clear_notification(self):
        self.notification_label.text = ""

    def load_ingredients(self):
        try:
            resp = requests.get("http://localhost:8000/ingredients", timeout=3)
            resp.raise_for_status()
            data = resp.json()
            self.ingredients_data = {item["ingredient"]: item for item in data}

            self.ingredient_list.clear_widgets()
            for item in data:
                self._add_row(item)
        except Exception as e:
            print("Error loading ingredients:", e)

    def _add_row(self, item):
        ing_name = item["ingredient"]
        qty      = round(item["quantity"], 2)
        unit     = item["unit"]
        pur_date = item["purchase_date"]
        exp_date = item["expiry_date"]

        label_text = f"{ing_name} {qty} {unit} (mua: {pur_date} | hạn: {exp_date})"
        box = BoxLayout(orientation='vertical', size_hint_y=None, height=80,
                        padding=(10, 5))

        label = Label(text=label_text, size_hint_y=None,
                      height=40, color=(0, 0, 0, 1))

        # buttons row
        line = BoxLayout(size_hint_y=None, height=40, spacing=10)
        use_inp = TextInput(hint_text="Nhập số", size_hint_x=.3,
                            input_filter="float")
        use_btn = RoundedButton(text="Sử dụng", size_hint_x=.35,
                                on_press=lambda *_:
                                self.use_ingredient(ing_name, use_inp))
        use_btn.change_color(233/255,150/255,14/255,1)
        use_btn.color = (0, 0, 0, 1)

        del_btn = RoundedButton(text="Xóa", size_hint_x=.35,
                                on_press=lambda *_:
                                self.delete_ingredient(ing_name))
        del_btn.change_color(233/255,150/255,14/255,1)
        del_btn.color = (0, 0, 0, 1)

        line.add_widget(use_inp)
        line.add_widget(use_btn)
        line.add_widget(del_btn)

        box.add_widget(label)
        box.add_widget(line)
        self.ingredient_list.add_widget(box)

    def use_ingredient(self, ingredient, input_field):
        amount_str = input_field.text.strip()
        if not self.is_valid_amount(amount_str, ingredient):
            self.show_notification("Vui lòng nhập số lượng hợp lệ!")
            return
        amount = float(amount_str)

        self.clear_notification()
        self.show_spinner()
        t = threading.Thread(target=self._use_worker,
                             args=(ingredient, amount), daemon=True)
        t.start()

    def _use_worker(self, ingredient, amount):
        try:
            url = f"http://localhost:8000/ingredients/{ingredient}"
            resp = requests.put(url, params={"used_amount": amount}, timeout=5)
            ok = resp.status_code == 200
            message = (f"Đã sử dụng {amount} "
                       f"{self.ingredients_data[ingredient]['unit']} {ingredient}"
                       if ok else "Lỗi từ server: " + resp.text)
        except Exception as e:
            ok = False
            message = f"Lỗi kết nối: {e}"

        Clock.schedule_once(lambda dt: self._after_use(message, ok))

    def _after_use(self, message, ok):
        self.hide_spinner()
        self.show_notification(message)
        if ok:
            self.load_ingredients()

    def is_valid_amount(self, s, ing):
        try:
            if not (s.isnumeric() or self.is_valid_float(s)):
                return False
            val = float(s)
            return 0 < val <= self.ingredients_data.get(ing, {}).get("quantity", 0)
        except ValueError:
            return False

    @staticmethod
    def is_valid_float(v):
        try:
            float(v)
            return True
        except ValueError:
            return False

    def delete_ingredient(self, ing):
        try:
            resp = requests.delete(f"http://localhost:8000/ingredients/{ing}",
                                   timeout=5)
            if resp.status_code == 200:
                self.show_notification(f"Đã xóa nguyên liệu: {ing}")
                self.load_ingredients()
            else:
                self.show_notification("Lỗi xóa: " + resp.text)
        except Exception as e:
            self.show_notification(f"Lỗi kết nối: {e}")

    def add_ingredient(self, *_):
        name = self.name_input.text.strip()
        quantity = self.quantity_input.text.strip()
        unit = self.unit_input.text.strip()
        date = self.date_input.text.strip()
        expiry = self.expiry_input.text.strip()
        if not (name and quantity and unit and date and expiry):
            self.show_notification("Điền đủ thông tin!")
            return
        try:
            body = {"name": name, "quantity": float(quantity),
                    "unit": unit, "purchase_date": date,
                    "expiry_date": expiry}
            resp = requests.post("http://localhost:8000/ingredients",
                                 json=body, timeout=5)
            if resp.status_code == 200:
                self.show_notification(f"Đã thêm nguyên liệu: {name}")
                self.load_ingredients()
            else:
                self.show_notification("Lỗi thêm: " + resp.text)
        except Exception as e:
            self.show_notification(f"Lỗi kết nối: {e}")


    def update_rect(self, *_):
        self.rect.size = self.size
        self.rect.pos = self.pos


class _Demo(MDApp):
    def build(self):
        return Ingredients()


if __name__ == '__main__':
    _Demo().run()
