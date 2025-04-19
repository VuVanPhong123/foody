from frontend.roundButton import RoundedButton
import requests  
import os
import pandas as pd 
import ast
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen, ScreenManager, FallOutTransition
from kivy.graphics import Color, Rectangle
from kivymd.uix.button import MDIconButton,MDFloatingActionButton
from kivymd.app import MDApp
from kivy.uix.popup import Popup
from frontend.settingsScreen import SettingsScreen
from frontend.geminiChatScreen import GeminiChatScreen  

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.menu_items = self.fetch_menu()
        self.selected_quantities = {item['name']: 0 for item in self.menu_items}
        self.quantity_inputs = {}

        self.layout = FloatLayout()
        self.scroll_view = ScrollView(size_hint=(0.98, 0.8), pos_hint={"center_x": 0.5, "center_y": 0.55})

        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll_view.add_widget(self.container)
        self.layout.add_widget(self.scroll_view)

        self.confirm_button = RoundedButton(
            text="Thêm vào giỏ hàng",
            size_hint=(None, None),
            size=(250, 50),
            pos_hint={"center_x": 0.5, "y": 0.02},
            font_size=18
        )
        self.confirm_button.change_color(0.9, 0.4, 0.1, 1)
        self.confirm_button.color = (0, 0, 0, 1)
        self.confirm_button.bind(on_press=self.save_to_cart)

        self.gemini_btn = MDFloatingActionButton(
            icon="robot",
            md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1),
            pos_hint={"x": 0.02, "y": 0.02}
        )
        self.gemini_btn.bind(on_press=self.open_gemini_chat)
        self.layout.add_widget(self.gemini_btn)

        self.layout.add_widget(self.confirm_button)
        self.add_widget(self.layout)

        self.populate_menu()

    def fetch_menu(self):
        try:
            resp = requests.get("http://localhost:8003/menu")
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print("Error fetching menu:", e)
        return []

    def populate_menu(self):
        for item in self.menu_items:
            name = item['name']
            price = item['price']
            image_path = item['image']
            if not os.path.exists(image_path):
                image_path = 'images/default.png'

            row_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=100)

            image = Image(source=image_path, size_hint=(0.2, 1))

            info_container = BoxLayout(orientation='vertical', size_hint=(0.4, 1), padding=5, spacing=2)
            with info_container.canvas.before:
                Color(245 / 255, 177 / 255, 67 / 255, 1)
                info_container.bg_rect = Rectangle(size=info_container.size, pos=info_container.pos)
            info_container.bind(size=self.update_bg_rect, pos=self.update_bg_rect)

            name_label = Label(text=name, size_hint=(1, 0.5), color=(0, 0, 0, 1), halign="left", valign="middle")
            price_label = Label(text=f"Giá: {price}đ", size_hint=(1, 0.5), color=(0, 0, 0, 1), halign="left", valign="middle")

            for lbl in [name_label, price_label]:
                lbl.bind(size=lbl.setter('text_size'))
                lbl.text_size = lbl.size

            info_container.add_widget(name_label)
            info_container.add_widget(price_label)

            control_box = BoxLayout(size_hint=(0.4, 1), spacing=5)
            minus_btn = Button(text="-", size_hint=(0.2, 1), background_color=(200 / 255, 50 / 255, 50 / 255, 1), color=(1, 1, 1, 1))
            quantity_input = TextInput(
                text="0",
                size_hint=(0.3, 1),
                multiline=False,
                halign="center"
            )
            quantity_input.bind(text=self.make_quantity_update_handler(name))
            quantity_input.bind(minimum_height=lambda instance, value: setattr(instance, 'padding', [0, (instance.height - instance.line_height) / 2]))
            self.quantity_inputs[name] = quantity_input

            plus_btn = Button(text="+", size_hint=(0.2, 1), background_color=(200 / 255, 50 / 255, 50 / 255, 1), color=(1, 1, 1, 1))

            minus_btn.bind(on_press=self.make_decrement_handler(name, quantity_input))
            plus_btn.bind(on_press=self.make_increment_handler(name, quantity_input))

            control_box.add_widget(minus_btn)
            control_box.add_widget(quantity_input)
            control_box.add_widget(plus_btn)

            row_box.add_widget(image)
            row_box.add_widget(info_container)
            row_box.add_widget(control_box)

            self.container.add_widget(row_box)

    def make_quantity_update_handler(self, name):
        def update_quantity(instance, value):
            try:
                quantity = max(0, int(value))
            except ValueError:
                quantity = 0
            self.selected_quantities[name] = quantity
        return update_quantity

    def make_increment_handler(self, name, input_field):
        return lambda btn: self.increment(name, input_field)

    def make_decrement_handler(self, name, input_field):
        return lambda btn: self.decrement(name, input_field)

    def increment(self, item, input_field):
        self.selected_quantities[item] += 1
        input_field.text = str(self.selected_quantities[item])

    def decrement(self, item, input_field):
        if self.selected_quantities[item] > 0:
            self.selected_quantities[item] -= 1
            input_field.text = str(self.selected_quantities[item])

    def save_to_cart(self, instance):
        check = any(qty > 0 for qty in self.selected_quantities.values())
        if not check:
            self.show_popup("Bạn chưa chọn gì!")
            return

        try:
            payload = {
                "quantities": self.selected_quantities,
                "menu_items": self.menu_items
            }
            resp = requests.post("http://localhost:8004/cart", json=payload)
            if resp.status_code == 200:
                self.show_popup("Đã thêm vào giỏ hàng!")
            else:
                self.show_popup("Lỗi khi thêm vào giỏ hàng.")
        except Exception as e:
            print("Error saving cart:", e)
            self.show_popup("Không thể kết nối đến máy chủ.")

        for name in self.selected_quantities:
            if name in self.quantity_inputs:
                self.quantity_inputs[name].text = "0"
                self.quantity_inputs[name].bind(text=self.make_quantity_update_handler(name))
            self.selected_quantities[name] = 0

    def show_popup(self, message):
        popup = Popup(
            title="Thông báo",
            content=Label(text=message),
            size_hint=(None, None),
            size=(300, 150),
            auto_dismiss=True
        )
        popup.open()

    def update_bg_rect(self, instance, value):
        instance.bg_rect.pos = instance.pos
        instance.bg_rect.size = instance.size
    def open_gemini_chat(self, instance):
        self.manager.current = "gemini"

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

class CartScreen(Screen):
    def __init__(self, **kwargs):
        super(CartScreen, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.layout = FloatLayout()
        self.scroll = ScrollView(size_hint=(0.98, 0.82), pos_hint={"center_x": 0.5, "center_y": 0.55})

        self.container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=10,
            padding=10
        )
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container)

        self.buy_all_button = RoundedButton(
            text="Mua tất cả",
            size_hint=(None, None),
            size=(250, 50),
            pos_hint={"center_x": 0.5, "y": 0.02},
            font_size=18
        )
        self.buy_all_button.change_color(0.9, 0.4, 0.1, 1)
        self.buy_all_button.bind(on_press=self.handle_buy_all)

        self.layout.add_widget(self.scroll)
        self.layout.add_widget(self.buy_all_button)
        self.add_widget(self.layout)

    def load_cart(self):
        self.container.clear_widgets()

        try:
            resp = requests.get("http://localhost:8004/cart")
            cart = resp.json()
        except Exception as e:
            self.container.add_widget(Label(text="Lỗi khi tải giỏ hàng: " + str(e)))
            return

        if not cart:
            self.container.add_widget(Label(
                text="Bạn không có gì trong giỏ hàng",
                color=(0, 0, 0, 1),
                font_size=18,
                size_hint=(1, None),
                height=40
            ))
            return

        for row in cart:
            item_names = row['item_names']
            quantities = row['quantities']

            if isinstance(item_names, str):
                item_names = ast.literal_eval(item_names)
            if isinstance(quantities, str):
                quantities = ast.literal_eval(quantities)

            order_lines = [f"{item} x{int(qty)}" for item, qty in zip(item_names, quantities)]
            order_info = "\n".join(order_lines)
            total_price = str(row['total_price'])

            order_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=5, spacing=5)
            order_box.height = 110 + (order_info.count('\n') * 18)

            top_row = BoxLayout(size_hint_y=0.6, spacing=10)

            order_btn = RoundedButton(
                text=order_info,
                size_hint=(0.7, 1),
                halign="left",
                valign="middle",
                text_size=(None, None)
            )
            order_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            order_btn.color = (0, 0, 0, 1)
            order_btn.bind(texture_size=order_btn.setter("size"))

            price_btn = RoundedButton(
                text=f"{total_price}đ",
                size_hint=(0.3, 1)
            )
            price_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            price_btn.color = (0, 0, 0, 1)

            mua_btn = Button(
                text="Mua",
                size_hint=(1, None),
                height=50,
                background_color=(233 / 255, 150 / 255, 14 / 255, 1),
                color=(0, 0, 0, 1),
            )
            mua_btn.bind(on_press=lambda _, row=row: self.show_order_popup([row]))

            top_row.add_widget(order_btn)
            top_row.add_widget(price_btn)
            order_box.add_widget(top_row)
            order_box.add_widget(mua_btn)

            self.container.add_widget(order_box)

    def show_order_popup(self, rows):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        name_input = TextInput(hint_text="Họ tên", size_hint_y=None, height=40)
        phone_input = TextInput(hint_text="Số điện thoại", size_hint_y=None, height=40)
        address_input = TextInput(hint_text="Địa chỉ", size_hint_y=None, height=40)
        note_input = TextInput(hint_text="Ghi chú", size_hint_y=None, height=60)

        confirm_button = Button(
            text="Xác nhận",
            size_hint=(1, None),
            height=50,
            background_color=(0.2, 0.6, 0.2, 1),
            color=(1, 1, 1, 1)
        )

        content.add_widget(name_input)
        content.add_widget(phone_input)
        content.add_widget(address_input)
        content.add_widget(note_input)
        content.add_widget(confirm_button)

        popup = Popup(title="Thông tin đơn hàng", content=content, size_hint=(None, None), size=(400, 450), auto_dismiss=True)

        confirm_button.bind(on_press=lambda _: self.confirm_order(
            popup,
            name_input.text,
            phone_input.text,
            address_input.text,
            note_input.text,
            rows
        ))

        popup.open()

    def confirm_order(self, popup, name, phone, address, note, rows):
        popup.dismiss()

        if not name.strip() or not phone.strip() or not address.strip():
            self.show_warning("Vui lòng điền đầy đủ họ tên, số điện thoại và địa chỉ.")
            return

        try:
            for row in rows:
                items = row['item_names']
                quantities = row['quantities']
                if isinstance(items, str):
                    items = ast.literal_eval(items)
                if isinstance(quantities, str):
                    quantities = ast.literal_eval(quantities)

                payload = {
                    "order": ", ".join([f"{item} x{qty}" for item, qty in zip(items, quantities)]),
                    "price": row['total_price'],
                    "name": name.strip(),
                    "address": address.strip(),
                    "note": note.strip(),
                    "phone": phone.strip()
                }

                requests.post("http://localhost:8005/orderinfo", json=payload)

                requests.delete("http://localhost:8004/cart", json={
                    "item_names": items,
                    "quantities": quantities,
                    "total_price": row['total_price']
                })

            self.show_warning("Đã gửi đơn hàng thành công.")
            self.load_cart()

        except Exception as e:
            self.show_warning("Lỗi: " + str(e))

    def handle_buy_all(self, instance):
        try:
            resp = requests.get("http://localhost:8004/cart")
            cart = resp.json()
        except Exception as e:
            self.show_warning("Không thể tải giỏ hàng: " + str(e))
            return

        if not cart:
            self.show_warning("Không có đơn hàng nào để mua.")
            return

        self.show_order_popup(cart)

    def show_warning(self, message):
        popup = Popup(
            title="Thông báo",
            content=Label(text=message),
            size_hint=(None, None),
            size=(350, 200)
        )
        popup.open()

    def on_pre_enter(self, *args):
        self.load_cart()

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
class OrderScreen(Screen):
    def __init__(self, **kwargs):
        super(OrderScreen, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.layout = FloatLayout()
        self.scroll = ScrollView(size_hint=(0.98, 0.92), pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.container.bind(minimum_height=self.container.setter('height'))

        self.scroll.add_widget(self.container)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def load_orders(self):
        self.container.clear_widgets()
        try:
            resp = requests.get("http://localhost:8005/orderinfo")
            data = resp.json()
        except Exception as e:
            self.container.add_widget(Label(text="Lỗi khi tải đơn hàng: " + str(e)))
            return

        if not data:
            self.container.add_widget(Label(
                text="Bạn không có đơn hàng nào",
                font_size=18,
                color=(0, 0, 0, 1),
                size_hint=(1, None),
                height=40
            ))
            return

        for idx, row in enumerate(data):
            order_text = str(row.get("order", "")).replace(",", "\n").strip()
            order_text = ' ' + order_text
            price = str(row.get("price", ""))

            order_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5, padding=5)

            top_row = BoxLayout(size_hint_y=None, spacing=10)

            
            order_btn = RoundedButton(
                text=order_text,
                size_hint=(0.7, None),
                halign="left",
                valign="middle",
                text_size=(None, None)
            )
            order_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            order_btn.color = (0, 0, 0, 1)

            order_btn.texture_update()
            height = order_btn.texture_size[1] + 20
            order_btn.height = height

            
            price_btn = RoundedButton(
                text=f"{price}đ",
                size_hint=(0.3, None),
                height=height,
            )
            price_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            price_btn.color = (0, 0, 0, 1)
            top_row.height = height
            top_row.add_widget(order_btn)
            top_row.add_widget(price_btn)

            change_btn = Button(
                text="Thay đổi thông tin",
                size_hint_y=None,
                height=40,
                background_color=(0.1, 0.3, 0.6, 1),
                color=(1, 1, 1, 1)
            )
            delete_btn = Button(
                text="Hủy đơn",
                size_hint_y=None,
                height=40,
                background_color=(0.7, 0.2, 0.2, 1),
                color=(1, 1, 1, 1)
            )

            change_btn.bind(on_press=lambda _, i=idx, r=row: self.show_edit_popup(i, r))
            delete_btn.bind(on_press=lambda _, i=idx: self.delete_order(i))

            order_box.add_widget(top_row)
            order_box.add_widget(change_btn)
            order_box.add_widget(delete_btn)
            order_box.height = height + 40 + 40 + 20

            self.container.add_widget(order_box)

    def show_edit_popup(self, index, row):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        name_input = TextInput(text=str(row.get("name", "")), hint_text="Họ tên", size_hint_y=None, height=40)
        phone_input = TextInput(text=str(row.get("phone", "")), hint_text="Số điện thoại", size_hint_y=None, height=40)
        address_input = TextInput(text=str(row.get("address", "")), hint_text="Địa chỉ", size_hint_y=None, height=40)
        note_input = TextInput(text=str(row.get("note", "")), hint_text="Ghi chú", size_hint_y=None, height=60)

        confirm_button = Button(
            text="Xác nhận",
            size_hint=(1, None),
            height=50,
            background_color=(0.2, 0.6, 0.2, 1),
            color=(1, 1, 1, 1)
        )

        content.add_widget(name_input)
        content.add_widget(phone_input)
        content.add_widget(address_input)
        content.add_widget(note_input)
        content.add_widget(confirm_button)

        popup = Popup(
            title="Chỉnh sửa đơn hàng",
            content=content,
            size_hint=(None, None),
            size=(400, 450),
            auto_dismiss=True
        )

        confirm_button.bind(
            on_press=lambda _: self.update_order(index, name_input.text, phone_input.text, address_input.text, note_input.text, row["order"], row["price"], popup)
        )

        popup.open()

    def update_order(self, index, name, phone, address, note, order, price, popup):
        popup.dismiss()
        payload = {
            "order": order,
            "price": price,
            "name": name,
            "address": address,
            "note": note,
            "phone": phone
            
        }
        try:
            requests.put(f"http://localhost:8005/orderinfo/{index}", json=payload)
            self.load_orders()
        except Exception as e:
            self.show_popup("Lỗi khi cập nhật: " + str(e))

    def delete_order(self, index):
        try:
            requests.delete(f"http://localhost:8005/orderinfo/{index}")
            self.load_orders()
        except Exception as e:
            self.show_popup("Lỗi khi xóa đơn hàng: " + str(e))

    def show_popup(self, message):
        popup = Popup(
            title="Thông báo",
            content=Label(text=message),
            size_hint=(None, None),
            size=(350, 200)
        )
        popup.open()

    def on_pre_enter(self, *args):
        self.load_orders()
        self.refresh_event = Clock.schedule_interval(lambda dt: self.load_orders(), 5)

    def on_leave(self, *args):
        if self.refresh_event:
            self.refresh_event.cancel()
            self.refresh_event = None

class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super(HistoryScreen, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.layout = BoxLayout(orientation='vertical', padding=5, spacing=5)
        self.scroll = ScrollView(size_hint=(1, 1))
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

        self.refresh_event = None

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def on_pre_enter(self, *args):
        self.load_history()
        self.refresh_event = Clock.schedule_interval(lambda dt: self.load_history(), 5)

    def on_leave(self, *args):
        if self.refresh_event:
            self.refresh_event.cancel()
            self.refresh_event = None

    def load_history(self):
        self.container.clear_widgets()
        try:
            resp = requests.get("http://localhost:8007/history")
            entries = resp.json()
        except Exception as e:
            self.container.add_widget(Label(text="Lỗi khi tải lịch sử: " + str(e)))
            return

        if not entries:
            self.container.add_widget(Label(
                text="Không có lịch sử đơn hàng",
                font_size=18,
                color=(0, 0, 0, 1)
            ))
            return

        for entry in entries:
            food = " " + entry.get("order", "").replace(", ", "\n").strip()
            price = f"{entry.get('price', 0)}đ"
            datetime_text = f"{entry.get('date', '--')}\n{entry.get('time', '--')}"
            status = entry.get("status", "")

            row_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
            top_row = BoxLayout(size_hint_y=None, spacing=10)

            time_btn = RoundedButton(
                text=datetime_text,
                size_hint=(0.2, None),
                halign="center",
                valign="middle",
                text_size=(None, None)
            )
            time_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            time_btn.color = (0, 0, 0, 1)
            time_btn.font_size = (self.width+self.height)/2 / 50

            order_btn = RoundedButton(
                text=food,
                size_hint=(0.6, None),
                halign="left",
                valign="middle",
                text_size=(None, None)
            )
            order_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            order_btn.color = (0, 0, 0, 1)

            price_btn = RoundedButton(text=price, size_hint=(0.2, None))
            price_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            price_btn.color = (0, 0, 0, 1)

            order_btn.texture_update()
            row_height = order_btn.texture_size[1] + 20
            order_btn.height = row_height
            time_btn.height = row_height
            price_btn.height = row_height
            top_row.height = row_height

            top_row.add_widget(time_btn)
            top_row.add_widget(order_btn)
            top_row.add_widget(price_btn)

            status_btn = Button(
                text=status,
                size_hint_y=None,
                height=40,
                background_color=(0.1, 0.6, 0.1, 1) if status == "Đã hoàn thành" else (0.8, 0.1, 0.1, 1),
                color=(1, 1, 1, 1)
            )

            row_box.add_widget(top_row)
            row_box.add_widget(status_btn)
            row_box.height = top_row.height + status_btn.height + 20  # full block height

            self.container.add_widget(row_box)

class MainScreenCus(Screen):
    def __init__(self, **kwargs):
        super(MainScreenCus, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.active_tab = None

        root = BoxLayout(orientation='vertical')

        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='50dp',
            padding=('10dp', '5dp'),
            spacing='10dp'
        )

        self.greeting_label = Label(
            text='FOODY',
            color=(0, 0, 0, 1),
            halign="left",
            valign="middle",
            size_hint=(0.4, 1)
        )
        self.greeting_label.bind(size=self.greeting_label.setter('text_size'))
        self.bind(size=self.update_font_size)

        settings_button = MDIconButton(
            icon="cog",
            md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1),
            icon_size="20sp",
        )
        settings_button.bind(on_press=self.go_to_settings)
        top_bar.add_widget(self.greeting_label)
        top_bar.add_widget(settings_button)

        tab_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='40dp'
        )

        self.tabs = [
            ("Menu", "menu_screen"),
            ("Giỏ hàng", "cart_screen"),
            ("Đơn hàng", "order_screen"),
            ("Lịch sử", "history_screen")
        ]

        self.buttons = []
        for text, screen_name in self.tabs:
            btn = RoundedButton(
                text=text,
                size_hint=(0.25, 1),
                font_size=(self.width + self.height)/2 / 20,
            )
            btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            btn.color=(0,0,0,1)
            btn.bind(on_press=lambda b, sn=screen_name: self.select_tab(b, sn))
            self.buttons.append(btn)
            tab_bar.add_widget(btn)

        self.bind(size=self.update_button_font_size)

        self.screen_manager = ScreenManager(transition=FallOutTransition())
        self.screen_manager.add_widget(MenuScreen(name="menu_screen"))
        self.screen_manager.add_widget(CartScreen(name="cart_screen"))
        self.screen_manager.add_widget(OrderScreen(name="order_screen"))
        self.screen_manager.add_widget(HistoryScreen(name="history_screen"))
        self.screen_manager.add_widget(GeminiChatScreen(name="gemini"))

        root.add_widget(top_bar)
        root.add_widget(tab_bar)
        root.add_widget(self.screen_manager)
        self.add_widget(root)

        if self.buttons:
            self.select_tab(self.buttons[0], "menu_screen")
    def select_tab(self, new_button, screen_name):
        if self.active_tab and self.active_tab != new_button:
            self.active_tab.change_color(233/255, 150/255, 14/255, 1)
            self.active_tab.color = (0, 0, 0, 1)

        new_button.change_color(200/255, 100/255, 14/255, 1)
        new_button.color = (0, 0, 0, 1)
        self.active_tab = new_button
        self.screen_manager.current = screen_name

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def update_font_size(self, *args):
        self.greeting_label.font_size = (self.width + self.height)/2 / 25
    def go_to_settings(self, instance):
        self.manager.current = "settings"
    def update_button_font_size(self, *args):
        for btn in self.buttons:
            btn.font_size = (self.width + self.height)/2 / 36
