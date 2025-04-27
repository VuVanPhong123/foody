import requests
import pandas as pd
from threading import Thread
from functools import partial

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivymd.app import MDApp

from frontend.roundButton import RoundedButton


class Makingorders(Screen):
    def __init__(self, top_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.top_manager = top_manager

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.menu_items = self.fetch_menu()
        self.selected_items = {item: 0 for item in self.menu_items}
        self.orders = []
        self.revenue = 0

        self.no_orders_label = Label(text="Bạn chưa có đơn hàng nào",
                                     size_hint=(None, None),
                                     pos_hint={"center_x": .5, "center_y": .5},
                                     color=(0, 0, 0, 1))
        self.add_widget(self.no_orders_label)

        self.create_order_btn = RoundedButton(text="+", size_hint=(.1, .07),
                                              font_size=15,
                                              pos_hint={"center_x": .1,
                                                        "center_y": .1})
        self.create_order_btn.change_color(233/255, 150/255, 14/255, 1)
        self.create_order_btn.bind(on_press=self.toggle_menu)
        self.add_widget(self.create_order_btn)

        self.layout = FloatLayout()
        self.add_widget(self.layout)

        self.scroll_view = ScrollView(size_hint=(.4, .5),
                                      pos_hint={"center_x": .7, "center_y": .5})
        self.menu_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.menu_layout.bind(minimum_height=self.menu_layout.setter('height'))
        self.scroll_view.add_widget(self.menu_layout)

        for item_name in (self.menu_items.keys()
                          if isinstance(self.menu_items, dict)
                          else self.menu_items):
            btn = Button(text=item_name, size_hint_y=None, height=50)
            btn.bind(on_press=self.add_to_order)
            self.menu_layout.add_widget(btn)

        self.complete_btn = Button(text="Hoàn thành",
                                   size_hint=(.4, .1),
                                   pos_hint={"center_x": .7, "center_y": .2},
                                   background_color=(233/255,150/255,14/255,1))
        self.complete_btn.bind(on_press=self.complete_order)

        self.scroll_view2 = ScrollView(size_hint=(.8, .7),
                                       pos_hint={"center_x": .5, "center_y": .5})
        self.order_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.order_layout.bind(minimum_height=self.order_layout.setter('height'))
        self.scroll_view2.add_widget(self.order_layout)
        self.layout.add_widget(self.scroll_view2)

        self.status_label = Label(text="", size_hint=(1, None), height=30,
                                  pos_hint={"x": 0, "y": 0}, color=(0, 0, 0, 1))
        self.layout.add_widget(self.status_label)

    def show_status(self, text):
        self.status_label.text = text

    def hide_status(self, *args):
        self.status_label.text = ""

    def fetch_menu(self):
        try:
            resp = requests.get("http://localhost:8001/menu", timeout=3)
            return resp.json() if resp.status_code == 200 else {}
        except Exception as e:
            print("Menu fetch error:", e)
            return {}

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def toggle_menu(self, _):
        if self.scroll_view.parent:
            self.layout.remove_widget(self.scroll_view)
            self.layout.remove_widget(self.complete_btn)
            self.create_order_btn.change_color(233/255, 150/255, 14/255, 1)
        else:
            self.layout.add_widget(self.scroll_view)
            self.layout.add_widget(self.complete_btn)
            self.create_order_btn.change_color(200/255, 100/255, 14/255, 1)
            self.selected_items = {item: 0 for item in self.selected_items}

    def add_to_order(self, btn):
        if btn.text in self.selected_items:
            self.selected_items[btn.text] += 1

    def complete_order(self, _):
        if not any(qty > 0 for qty in self.selected_items.values()):
            return

        self.show_status("đang tải...")

        items_snapshot = self.selected_items.copy()

        Thread(target=self._complete_order_worker,
               args=(items_snapshot,), daemon=True).start()

        self.toggle_menu(None)  

    def _complete_order_worker(self, items_snapshot):
        """Runs in background thread."""
        try:
            resp = requests.post("http://localhost:8001/orders",
                                 json={"items": items_snapshot}, timeout=5)
            resp.raise_for_status()
            total_price = resp.json().get("total_price", 0)
        except Exception as e:
            print("Order service error:", e)
            Clock.schedule_once(self.hide_status)
            return

        Clock.schedule_once(partial(self._add_order_row,
                                    items_snapshot, total_price))

    def _add_order_row(self, items_snapshot, total_price, dt):
        header = f"Đơn hàng {len(self.orders)+1} (Tổng: {total_price}đ):"
        lines  = [f"{it} x{qt}" for it, qt in items_snapshot.items() if qt > 0]
        items_str = "\n".join(lines)
        order_text = f"{header}\n{items_str}"
        self.orders.append(order_text)

        row_box = BoxLayout(orientation='horizontal', size_hint_y=None)
        row_box.bind(minimum_height=row_box.setter('height'))

        done_btn = Button(text="Xong", size_hint=(.25, 1),
                          background_color=(233/255,150/255,14/255,1))
        cancel_btn = Button(text="Hủy", size_hint=(.25, 1),
                            background_color=(233/255,150/255,14/255,1))
        order_btn = Button(text=order_text, size_hint=(.5, None),
                           background_color=(233/255,150/255,14/255,1),
                           halign="left", valign="middle")
        order_btn.bind(texture_size=lambda b, s: setattr(b, "height", s[1] + 20))
        order_btn.bind(size=lambda b, s: setattr(b, "text_size",
                                                 (s[0]-20 if s[0] > 20 else 0, None)))

        row_box.add_widget(done_btn)
        row_box.add_widget(cancel_btn)
        row_box.add_widget(order_btn)
        self.order_layout.add_widget(row_box)

        done_btn.bind(on_press=lambda _:
                      self.complete_revenue(items_str, total_price, row_box))
        cancel_btn.bind(on_press=lambda _:
                        self.remove_order(row_box))

        self.no_orders_label.opacity = 0
        self.hide_status()

    def complete_revenue(self, done_orders, total_price, row_box):
        self.show_status("đang thêm vào doanh thu...")

        Thread(target=self._revenue_worker,
               args=(done_orders, total_price, row_box), daemon=True).start()

    def _revenue_worker(self, done_orders, total_price, row_box):
        try:
            now = pd.Timestamp.now()
            payload = {
                "done_orders": done_orders.replace("\n", ", "),
                "price": total_price,
                "time": now.strftime("%H:%M:%S"),
                "date": now.strftime("%Y-%m-%d")
            }
            resp = requests.post("http://localhost:8002/revenue",
                                 json=payload, timeout=5)
            resp.raise_for_status()
        except Exception as e:
            print("Revenue post error:", e)
            Clock.schedule_once(self.hide_status)
            return

        Clock.schedule_once(partial(self._after_revenue_ok, row_box))

    def _after_revenue_ok(self, row_box, dt):
        self.revenue += 0  
        if self.top_manager:
            try:
                rev_screen = self.top_manager.get_screen("doanh_thu")
                rev_screen.refresh_data()
            except Exception as e:
                print("Could not refresh revenue:", e)

        self.remove_order(row_box)
        self.hide_status()

    def remove_order(self, order_widget):
        self.order_layout.remove_widget(order_widget)
        if not self.order_layout.children:
            self.no_orders_label.opacity = 1


class DemoApp(MDApp):
    def build(self):
        return Makingorders()


if __name__ == '__main__':
    DemoApp().run()
