import threading, requests
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivymd.uix.spinner import MDSpinner

from frontend.roundButton import RoundedButton


class Onlineorders(Screen):
    ENDPOINT      = "http://localhost:8006/onlineorders"
    AUTO_REFRESH  = 15 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.layout = BoxLayout(orientation='vertical', spacing=5, padding=5)
        self.scroll = ScrollView(size_hint=(1, .95))
        self.container = BoxLayout(orientation='vertical', size_hint_y=None,
                                   spacing=10, padding=10)
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

        self.spinner      = None
        self.refresh_ev   = None

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

    def on_pre_enter(self, *_):
        self._load_async()
        self.refresh_ev = Clock.schedule_interval(lambda dt: self._load_async(),
                                                  self.AUTO_REFRESH)

    def on_leave(self, *_):
        if self.refresh_ev:
            self.refresh_ev.cancel()
            self.refresh_ev = None

    def update_rect(self, *_):
        self.rect.size = self.size
        self.rect.pos  = self.pos

    def _load_async(self):
        self.show_spinner()
        threading.Thread(target=self._fetch_worker, daemon=True).start()

    def _fetch_worker(self):
        try:
            orders = requests.get(self.ENDPOINT, timeout=5).json()
            error  = None
        except Exception as e:
            orders, error = None, str(e)

        Clock.schedule_once(lambda dt: self._after_fetch(orders, error))

    def _after_fetch(self, orders, error):
        self.hide_spinner()
        self.container.clear_widgets()

        if error:
            self.container.add_widget(
                Label(text=f"Lỗi khi tải đơn hàng: {error}",
                      color=(1, 0, 0, 1)))
            return

        if not orders:
            self.container.add_widget(
                Label(text="Không có đơn hàng online",
                      font_size=18, color=(0, 0, 0, 1)))
            return

        for idx, order in enumerate(orders):
            self._add_order_row(idx, order)

    def _add_order_row(self, idx, order):
        food  = order['order'].replace(", ", ",").replace(",", "\n").strip()
        price = f"{order['price']}đ"

        row_box = BoxLayout(orientation='vertical', size_hint_y=None,
                            spacing=10, padding=10)
        row_box.bind(minimum_height=row_box.setter("height"))

        top_row = BoxLayout(size_hint_y=None, spacing=10)
        top_row.bind(minimum_height=top_row.setter("height"))

        order_btn = RoundedButton(text=food, size_hint=(.65, None),
                                  halign="left", valign="middle",
                                  text_size=(None, None))
        order_btn.change_color(233/255,150/255,14/255,1)
        order_btn.color = (0, 0, 0, 1)

        price_btn = RoundedButton(text=price, size_hint=(.35, None))
        price_btn.change_color(233/255,150/255,14/255,1)
        price_btn.color = (0, 0, 0, 1)

        order_btn.bind(texture_size=lambda b, s: [
            setattr(order_btn, 'height', max(20, s[1] + 20)),
            setattr(price_btn, 'height', max(20, s[1] + 20))
        ])

        top_row.add_widget(order_btn)
        top_row.add_widget(price_btn)

        action_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
        done_btn = Button(text="Xong", background_color=(.2, .6, .2, 1),
                          color=(1, 1, 1, 1), size_hint=(.5, 1))
        cancel_btn = Button(text="Hủy đơn hàng", background_color=(.8, .2, .2, 1),
                            color=(1, 1, 1, 1), size_hint=(.5, 1))

        done_btn.bind(on_press=lambda *_: self._action_async("done", idx))
        cancel_btn.bind(on_press=lambda *_: self._action_async("cancel", idx))

        action_row.add_widget(done_btn)
        action_row.add_widget(cancel_btn)

        info_btn = Button(text="Thông tin đơn hàng", size_hint_y=None,
                          height=40, background_color=(.1, .4, .7, 1),
                          color=(1, 1, 1, 1))
        info_btn.bind(on_press=lambda *_: self.show_info_popup(order))

        row_box.add_widget(top_row)
        row_box.add_widget(action_row)
        row_box.add_widget(info_btn)
        self.container.add_widget(row_box)

    def _action_async(self, action, idx):
        self.show_spinner()
        threading.Thread(target=self._action_worker,
                         args=(action, idx), daemon=True).start()

    def _action_worker(self, action, idx):
        try:
            if action == "done":
                requests.put(f"{self.ENDPOINT}/{idx}", timeout=5)
            else:
                requests.delete(f"{self.ENDPOINT}/{idx}", timeout=5)
            error = None
        except Exception as e:
            error = str(e)
        Clock.schedule_once(lambda dt: self._after_action(error))

    def _after_action(self, error):
        self.hide_spinner()
        if error:
            self.show_error(f"Lỗi thao tác: {error}")
        self._load_async()  

    def show_info_popup(self, order):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        for key in ['name', 'phone', 'address', 'note']:
            content.add_widget(Label(text=f"{key.capitalize()}: {order.get(key,'')}",
                                     color=(1, 1, 1, 1)))
        Popup(title="Chi tiết đơn hàng", content=content,
              size_hint=(None, None), size=(400, 300)).open()

    def show_error(self, msg):
        Popup(title="Lỗi", content=Label(text=msg),
              size_hint=(None, None), size=(350, 200)).open()
