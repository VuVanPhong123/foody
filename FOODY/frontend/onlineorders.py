from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from frontend.roundButton import RoundedButton
import requests

class Onlineorders(Screen):
    def __init__(self, **kwargs):
        super(Onlineorders, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.layout = BoxLayout(orientation='vertical', spacing=5, padding=5)
        self.scroll = ScrollView(size_hint=(1, 0.95))
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
        self.load_orders()
        self.refresh_event = Clock.schedule_interval(lambda dt: self.load_orders(), 5)

    def on_leave(self, *args):
        if self.refresh_event:
            self.refresh_event.cancel()
            self.refresh_event = None

    def load_orders(self):
        self.container.clear_widgets()
        try:
            resp = requests.get("http://localhost:8006/onlineorders")
            orders = resp.json()
        except Exception as e:
            self.container.add_widget(Label(text=f"Error loading orders: {e}", color=(1, 0, 0, 1)))
            return

        if not orders:
            self.container.add_widget(Label(text="Không có đơn hàng online", font_size=18, color=(0, 0, 0, 1)))
            return

        for idx, order in enumerate(orders):
            food = order['order'].replace(", ", ",").replace(",", "\n").strip()
            price = f"{order['price']}đ"

            row_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
            row_box.bind(minimum_height=row_box.setter("height"))


            top_row = BoxLayout(size_hint_y=None, spacing=10)
            top_row.bind(minimum_height=top_row.setter("height"))
            order_btn = RoundedButton(
                text=food,
                size_hint=(0.65, None),
                halign="left",
                valign="middle",
                text_size=(None, None)
            )
            order_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            order_btn.color = (0, 0, 0, 1)

            price_btn = RoundedButton(
                text=price,
                size_hint=(0.35, None),
            )
            price_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            price_btn.color = (0, 0, 0, 1)

            order_btn.bind(
                texture_size=lambda btn, sz: [
                    setattr(order_btn, 'height', max(20, sz[1] + 20)),
                    setattr(price_btn, 'height', max(20, sz[1] + 20))
                ]
            )

            top_row.add_widget(order_btn)
            top_row.add_widget(price_btn)

            action_row = BoxLayout(size_hint_y=None, height=40, spacing=10)

            done_btn = Button(
                text="Xong",
                background_color=(0.2, 0.6, 0.2, 1),
                color=(1, 1, 1, 1),
                size_hint=(0.5, 1)
            )
            cancel_btn = Button(
                text="Hủy đơn hàng",
                background_color=(0.8, 0.2, 0.2, 1),
                color=(1, 1, 1, 1),
                size_hint=(0.5, 1)
            )

            done_btn.bind(on_press=lambda _, i=idx: self.mark_done(i))
            cancel_btn.bind(on_press=lambda _, i=idx: self.cancel_order(i))

            action_row.add_widget(done_btn)
            action_row.add_widget(cancel_btn)

            # Info row
            info_btn = Button(
                text="Thông tin đơn hàng",
                size_hint_y=None,
                height=40,
                background_color=(0.1, 0.4, 0.7, 1),
                color=(1, 1, 1, 1)
            )
            info_btn.bind(on_press=lambda _, o=order: self.show_info_popup(o))

            row_box.add_widget(top_row)
            row_box.add_widget(action_row)
            row_box.add_widget(info_btn)
            self.container.add_widget(row_box)

    def mark_done(self, index):
        try:
            requests.put(f"http://localhost:8006/onlineorders/{index}")
            self.load_orders()
        except Exception as e:
            self.show_error(f"Lỗi khi hoàn tất đơn: {e}")

    def cancel_order(self, index):
        try:
            requests.delete(f"http://localhost:8006/onlineorders/{index}")
            self.load_orders()
        except Exception as e:
            self.show_error(f"Lỗi khi hủy đơn: {e}")

    def show_info_popup(self, order):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        for key in ['name', 'phone', 'address', 'note']:
            content.add_widget(Label(
                text=f"{key.capitalize()}: {order.get(key, '')}",
                color=(1, 1, 1, 1)
            ))

        popup = Popup(
            title="Chi tiết đơn hàng",
            content=content,
            size_hint=(None, None),
            size=(400, 300)
        )
        popup.open()

    def show_error(self, message):
        popup = Popup(
            title="Lỗi",
            content=Label(text=message),
            size_hint=(None, None),
            size=(350, 200)
        )
        popup.open()
