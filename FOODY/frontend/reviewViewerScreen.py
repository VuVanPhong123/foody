import threading, requests
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivymd.uix.spinner import MDSpinner

from frontend.roundButton import RoundedButton


class ReviewViewerScreen(Screen):
    ENDPOINT      = "http://localhost:8008/review"
    AUTO_REFRESH  = 30  

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.avg_label = Label(text="", font_size=18, size_hint_y=None,
                               height=30, color=(0, 0, 0, 1))
        self.layout.add_widget(self.avg_label)

        self.scroll = ScrollView()
        self.container = BoxLayout(orientation='vertical', size_hint_y=None,
                                   spacing=10, padding=10)
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

        self.spinner = None
        self.refresh_ev = None

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

    def update_rect(self, *_):
        self.rect.size = self.size
        self.rect.pos  = self.pos

    def on_pre_enter(self, *_):
        self._load_async()
        self.refresh_ev = Clock.schedule_interval(lambda dt: self._load_async(),
                                                  self.AUTO_REFRESH)

    def on_leave(self, *_):
        if self.refresh_ev:
            self.refresh_ev.cancel()
            self.refresh_ev = None

    def _load_async(self):
        self.show_spinner()
        self.avg_label.text = "Đang tải đánh giá…"
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            resp = requests.get(self.ENDPOINT, timeout=5)
            resp.raise_for_status()
            reviews = resp.json()
            error = None
        except Exception as e:
            reviews, error = None, str(e)

        Clock.schedule_once(lambda dt: self._after_load(reviews, error))

    def _after_load(self, reviews, error):
        self.hide_spinner()
        self.container.clear_widgets()

        if error:
            self.avg_label.text = "Lỗi khi tải đánh giá"
            self.container.add_widget(Label(text=f"Lỗi: {error}",
                                            color=(1, 0, 0, 1)))
            return

        if not reviews:
            self.avg_label.text = "Chưa có đánh giá nào"
            self.container.add_widget(Label(text="Chưa có đánh giá nào",
                                            font_size=18, color=(0, 0, 0, 1)))
            return

        avg = sum(r["stars"] for r in reviews) / len(reviews)
        self.avg_label.text = (f"Đánh giá trung bình: {avg:.1f} sao "
                               f"({len(reviews)} đánh giá)")

        for r in reviews:
            stars, comment = r["stars"], r["comment"]

            probe = RoundedButton(text=comment, size_hint=(.7, None),
                                  text_size=(self.width * .65, None))
            probe.texture_update()
            h = probe.texture_size[1] + 20

            comment_btn = RoundedButton(text=comment, size_hint=(.7, None),
                                        height=h, halign="left", valign="middle")
            comment_btn.change_color(233/255,150/255,14/255,1)
            comment_btn.color = (0, 0, 0, 1)
            comment_btn.text_size = (self.width * .65 - 20, None)

            stars_btn   = RoundedButton(text=f"{stars} stars", size_hint=(.3, None),
                                        height=h)
            stars_btn.change_color(233/255,150/255,14/255,1)
            stars_btn.color = (0, 0, 0, 1)

            row = BoxLayout(size_hint_y=None, height=h, spacing=10)
            row.add_widget(stars_btn)
            row.add_widget(comment_btn)
            self.container.add_widget(row)
