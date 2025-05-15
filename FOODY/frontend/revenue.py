import requests
from threading import Thread

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivymd.app import MDApp


class Revenue(Screen):
    BASE_URL      = "http://localhost:8002/revenue"
    AUTO_REFRESH  = 30  
    ENDPOINT_MAP  = {
        "day":   "daily",
        "week":  "weekly",
        "month": "monthly",
        "total": "total",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.main_layout = BoxLayout(orientation="vertical", spacing=5, padding=5)
        self.add_widget(self.main_layout)

        self.period_bar = BoxLayout(size_hint_y=None, height="50dp", spacing=5)
        self.main_layout.add_widget(self.period_bar)

        self.btns = {}
        for text, p in [("Ngày", "day"), ("Tuần", "week"),
                        ("Tháng", "month"), ("Tổng", "total")]:
            b = Button(text=text,
                       background_color=(233/255,150/255,14/255,1),
                       color=(1,1,1,1))
            b.bind(on_press=lambda btn, period=p: self.select_period(btn, period))
            self.period_bar.add_widget(b)
            self.btns[p] = b

        self.scroll = ScrollView()
        self.main_layout.add_widget(self.scroll)

        self.table_layout = BoxLayout(orientation="vertical", size_hint_y=None)
        self.table_layout.bind(minimum_height=self.table_layout.setter("height"))
        self.scroll.add_widget(self.table_layout)

        self.total_label = Label(size_hint_y=None, height="40dp",
                                 font_size="18sp", color=(0, 0, 0,1))
        self.main_layout.add_widget(self.total_label)

        self.active_btn = None
        self.period     = "day"
        self.cache      = {}
        self.refresh_ev = None

        self.select_period(self.btns["day"], "day")

    def on_pre_enter(self, *args):
        self._auto_refresh(0)
        self.refresh_ev = Clock.schedule_interval(self._auto_refresh,
                                                  self.AUTO_REFRESH)

    def on_leave(self, *args):
        if self.refresh_ev:
            self.refresh_ev.cancel()
            self.refresh_ev = None

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos  = self.pos

    def format_money(self, val: int) -> str:
        return f"{val:,}".replace(",", ".")

    def select_period(self, button, period):
        if self.active_btn and self.active_btn is not button:
            self.active_btn.background_color = (233/255,150/255,14/255,1)
        button.background_color = (100/255,200/255,14/255,1)
        self.active_btn = button
        self.period     = period

        self.build_table(self.cache.get(period, None))   
        self._fetch_async(period)                        

    def _auto_refresh(self, dt):
        self._fetch_async(self.period)

    def _fetch_async(self, period):
        def worker():
            try:
                ep  = self.ENDPOINT_MAP[period]
                url = f"{self.BASE_URL}/{ep}"
                data = requests.get(url, timeout=3).json()
            except Exception as e:
                print("Revenue fetch error:", e)
                data = {"rows": [], "total_sum": 0}
            Clock.schedule_once(lambda dt: self._on_data(period, data))
        Thread(target=worker, daemon=True).start()

    def _on_data(self, period, data):
        self.cache[period] = data
        if self.period == period:
            self.build_table(data)

    def build_table(self, data):
        self.table_layout.clear_widgets()
        if not data or not data.get("rows"):
            self.total_label.text = "Không có dữ liệu doanh thu"
            return

        rows      = data["rows"]
        total_sum = data["total_sum"]
        bg        = (233/255,150/255,14/255,1)

        def mk_row():
            row = BoxLayout(size_hint_y=None)
            row.bind(minimum_height=row.setter("height"))
            return row

        if self.period == "day":
            for r in rows:
                row = mk_row()
                items = "\n".join(r["done_orders"].split(", "))
                btn_items = Button(text=items, size_hint=(0.65, None),
                                   background_color=bg, color=(1,1,1,1),
                                   halign="left", valign="middle",
                                   text_size=(220, None))
                btn_items.bind(texture_size=lambda b, s:
                               setattr(b, "height", s[1] + 20))

                btn_time = Button(text=r["time"], size_hint=(0.15, 1),
                                  background_color=bg, color=(1,1,1,1),
                                  halign="center", valign="middle")
                btn_time.bind(size=lambda b, s:
                              setattr(b, "text_size", (s[0], None)))

                btn_price = Button(text=self.format_money(int(r["price"])),
                                   size_hint=(0.2, 1), background_color=bg,
                                   color=(1,1,1,1), halign="center", valign="middle")
                btn_price.bind(size=lambda b, s:
                               setattr(b, "text_size", (s[0], None)))

                row.add_widget(btn_items)
                row.add_widget(btn_time)
                row.add_widget(btn_price)
                self.table_layout.add_widget(row)

            self.total_label.text = f"Doanh thu hôm nay: {self.format_money(total_sum)} VND"

        elif self.period == "week":
            for r in rows:
                row = mk_row()
                left = f"{r['day_name_vi']} {r['day']}/{r['month']}/{r['year']}"
                btn_left = Button(text=left, size_hint=(0.5, 1),
                                  background_color=bg, color=(1,1,1,1),
                                  halign="center", valign="middle")
                btn_left.bind(size=lambda b, s:
                              setattr(b, "text_size", (s[0], None)))

                btn_right = Button(text=self.format_money(r["price"]),
                                   size_hint=(0.5, 1), background_color=bg,
                                   color=(1,1,1,1), halign="center", valign="middle")
                btn_right.bind(size=lambda b, s:
                               setattr(b, "text_size", (s[0], None)))

                row.add_widget(btn_left)
                row.add_widget(btn_right)
                self.table_layout.add_widget(row)

            self.total_label.text = f"Doanh thu tuần này: {self.format_money(total_sum)} VND"

        elif self.period == "month":
            for r in rows:
                row = mk_row()
                left = f"Ngày {r['day']}/{r['month']}/{r['year']}"
                btn_left = Button(text=left, size_hint=(0.5, 1),
                                  background_color=bg, color=(1,1,1,1),
                                  halign="center", valign="middle")
                btn_left.bind(size=lambda b, s:
                              setattr(b, "text_size", (s[0], None)))

                btn_right = Button(text=self.format_money(r["price"]),
                                   size_hint=(0.5, 1), background_color=bg,
                                   color=(1,1,1,1), halign="center", valign="middle")
                btn_right.bind(size=lambda b, s:
                               setattr(b, "text_size", (s[0], None)))

                row.add_widget(btn_left)
                row.add_widget(btn_right)
                self.table_layout.add_widget(row)

            self.total_label.text = f"Doanh thu tháng này: {self.format_money(total_sum)} VND"

        else: 
            for r in rows:
                row = mk_row()
                btn_left = Button(text=r["year_month"], size_hint=(0.5, 1),
                                  background_color=bg, color=(1,1,1,1),
                                  halign="center", valign="middle")
                btn_left.bind(size=lambda b, s:
                              setattr(b, "text_size", (s[0], None)))

                btn_right = Button(text=self.format_money(r["price"]),
                                   size_hint=(0.5, 1), background_color=bg,
                                   color=(1,1,1,1), halign="center", valign="middle")
                btn_right.bind(size=lambda b, s:
                               setattr(b, "text_size", (s[0], None)))

                row.add_widget(btn_left)
                row.add_widget(btn_right)
                self.table_layout.add_widget(row)

            self.total_label.text = f"Tổng doanh thu: {self.format_money(total_sum)} VND"


class _Demo(MDApp):
    def build(self):
        return Revenue()


if __name__ == "__main__":
    _Demo().run()
