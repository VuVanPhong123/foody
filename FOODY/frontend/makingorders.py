import requests
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from kivymd.app import MDApp

from frontend.roundButton import RoundedButton


class Makingorders(Screen):
    def __init__(self, top_manager=None, **kwargs):
        super(Makingorders, self).__init__(**kwargs)
        self.top_manager = top_manager
        with self.canvas.before:
            Color(245/255, 177/255, 67/255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.menu_items = self.fetch_menu()  
        self.selected_items = {item: 0 for item in self.menu_items}
        self.orders = []
        self.revenue = 0

        self.no_orders_label = Label(
            text="Bạn chưa có đơn hàng nào",
            size_hint=(None, None),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        self.no_orders_label.color=(0, 0, 0, 1)
        self.add_widget(self.no_orders_label)

        self.create_order_btn = RoundedButton(
            text="+",
            size_hint=(0.1, 0.07),
            font_size=15,
            pos_hint={"center_x": 0.1, "center_y": 0.1}
        )
        self.create_order_btn.change_color(233/255, 150/255, 14/255, 1)
        self.create_order_btn.bind(on_press=self.toggle_menu)
        self.add_widget(self.create_order_btn)

        self.layout = FloatLayout()

        self.scroll_view = ScrollView(size_hint=(0.4, 0.5), pos_hint={"center_x": 0.7, "center_y": 0.5})
        self.menu_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.menu_layout.bind(minimum_height=self.menu_layout.setter('height'))
        self.scroll_view.add_widget(self.menu_layout)

        if isinstance(self.menu_items, dict):
            for item_name in self.menu_items.keys():
                btn = Button(text=item_name, size_hint_y=None, height=50)
                btn.bind(on_press=self.add_to_order)
                self.menu_layout.add_widget(btn)
        elif isinstance(self.menu_items, list):
            for item_name in self.menu_items:
                btn = Button(text=item_name, size_hint_y=None, height=50)
                btn.bind(on_press=self.add_to_order)
                self.menu_layout.add_widget(btn)

        self.complete_btn = Button(
            text="Hoàn thành",
            size_hint=(0.4, 0.1),
            pos_hint={"center_x": 0.7, "center_y": 0.2},
            background_color=(233/255, 150/255, 14/255, 1)
        )
        self.complete_btn.bind(on_press=self.complete_order)

        self.scroll_view2 = ScrollView(size_hint=(0.8, 0.7), pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.order_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.order_layout.bind(minimum_height=self.order_layout.setter('height'))
        self.scroll_view2.add_widget(self.order_layout)

        self.layout.add_widget(self.scroll_view2)
        self.add_widget(self.layout)
        
    def fetch_menu(self):
        try:
            url = "http://localhost:8001/menu"
            resp = requests.get(url)
            if resp.status_code == 200:
                return resp.json()  # might be a dict or list
            else:
                print("Error fetching menu:", resp.text)
                return {}
        except Exception as e:
            print("Exception fetching menu:", e)
            return {}

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def toggle_menu(self, instance):
        if self.scroll_view.parent:
            self.layout.remove_widget(self.scroll_view)
            self.layout.remove_widget(self.complete_btn)
            self.create_order_btn.change_color(233/255, 150/255, 14/255, 1)
        else:
            self.layout.add_widget(self.scroll_view)
            self.layout.add_widget(self.complete_btn)
            self.create_order_btn.change_color(200/255, 100/255, 14/255, 1)

            if isinstance(self.menu_items, dict):
                self.selected_items = {item: 0 for item in self.menu_items.keys()}
            else:
                self.selected_items = {item: 0 for item in self.menu_items}

    def add_to_order(self, instance):
        item_name = instance.text
        if item_name in self.selected_items:
            self.selected_items[item_name] += 1

    def complete_order(self, instance):

        if any(qty > 0 for qty in self.selected_items.values()):
            url = "http://localhost:8001/orders"
            payload = {"items": self.selected_items}
            try:
                
                resp = requests.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    total_price = data.get("total_price", 0)
                else:
                    print("Error from Order Service:", resp.text)
                    return
            except Exception as e:
                print("Exception calling Order Service:", e)
                return

            header = f"Đơn hàng {len(self.orders) + 1} (Tổng: {total_price}đ):"
            lines = [f"{it} x{qt}" for it, qt in self.selected_items.items() if qt > 0]
            items_str = "\n".join(lines)
            order_text = f"{header}\n{items_str}"
            self.orders.append(order_text)

            row_box = BoxLayout(orientation='horizontal', size_hint_y=None)
            row_box.bind(minimum_height=row_box.setter('height'))

            done_btn = Button(
                text="Xong",
                size_hint=(0.25, 1),
                halign="center",
                valign="middle",
                background_color=(233/255, 150/255, 14/255, 1)
            )
            done_btn.bind(size=lambda b, sz: setattr(b, 'text_size', (sz[0], None)))

            cancel_btn = Button(
                text="Hủy",
                size_hint=(0.25, 1),
                halign="center",
                valign="middle",
                background_color=(233/255, 150/255, 14/255, 1)
            )
            cancel_btn.bind(size=lambda b, sz: setattr(b, 'text_size', (sz[0], None)))

            order_btn = Button(
                text=order_text,
                size_hint=(0.5, None),
                halign="left",
                valign="middle",
                background_color=(233/255, 150/255, 14/255, 1),
            )

            def on_texture_size(btn, tex_size):
                btn.height = tex_size[1] + 20
            order_btn.bind(texture_size=on_texture_size)

            def on_size(btn, size):
                new_width = size[0] - 20
                if new_width < 0:
                    new_width = 0
                btn.text_size = (new_width, None)
            order_btn.bind(size=on_size)

            row_box.add_widget(done_btn)
            row_box.add_widget(cancel_btn)
            row_box.add_widget(order_btn)
            self.order_layout.add_widget(row_box)
            done_btn.bind(on_press=lambda x: self.complete_revenue(items_str, total_price, row_box))
            cancel_btn.bind(on_press=lambda x: self.remove_order(row_box))

            self.no_orders_label.opacity = 0

        self.toggle_menu(None)

    def complete_revenue(self, done_orders, total_price, row_box):

        self.revenue += total_price
        if self.top_manager:
            try:
                rev_screen = self.top_manager.get_screen("doanh_thu")
                rev_screen.refresh_data()
            except Exception as e:
                print("Could not refresh revenue:", e)

        self.remove_order(row_box)

    def remove_order(self, order_widget):
        self.order_layout.remove_widget(order_widget)
        if len(self.order_layout.children) == 0:
            self.no_orders_label.opacity = 1


class DemoApp(MDApp):
    def build(self):
        return Makingorders()

if __name__ == '__main__':
    DemoApp().run()
