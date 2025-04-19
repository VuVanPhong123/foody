from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from frontend.roundButton import RoundedButton
from kivy.clock import Clock
import requests

class ReviewViewerScreen(Screen):
    def __init__(self, **kwargs):
        super(ReviewViewerScreen, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.avg_label = Label(
            text="Đang tính toán...",
            font_size=18,
            size_hint_y=None,
            height=30,
            color=(0, 0, 0, 1)
        )
        self.layout.add_widget(self.avg_label)

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
        self.load_reviews()
        self.refresh_event = Clock.schedule_interval(lambda dt: self.load_reviews(), 5)
    def on_leave(self, *args):
        if self.refresh_event:
            self.refresh_event.cancel()
            self.refresh_event = None
    def load_reviews(self):
        self.container.clear_widgets()
        try:
            resp = requests.get("http://localhost:8008/review")
            reviews = resp.json()
        except Exception as e:
            self.avg_label.text = "Lỗi khi tải đánh giá"
            self.container.add_widget(Label(text=f"Lỗi tải đánh giá: {e}", color=(1, 0, 0, 1)))
            return

        if not reviews:
            self.avg_label.text = "Chưa có đánh giá nào"
            self.container.add_widget(Label(text="Chưa có đánh giá nào", font_size=18, color=(0, 0, 0, 1)))
            return

        total_stars = sum(r.get("stars", 0) for r in reviews)
        avg_stars = total_stars / len(reviews)
        self.avg_label.text = f"Đánh giá trung bình: {avg_stars:.1f} sao ({len(reviews)} đánh giá)"

        for review in reviews:
            stars = review.get("stars", 0)
            comment = review.get("comment", "")

            temp_btn = RoundedButton(
                text=comment,
                size_hint=(0.7, None),
                halign="left",
                valign="middle",
                text_size=(self.width * 0.65, None)
            )
            temp_btn.texture_update()
            calculated_height = temp_btn.texture_size[1] + 20

            comment_btn = RoundedButton(
                text=comment,
                size_hint=(0.7, None),
                height=calculated_height,
                halign="left",
                valign="middle"
            )
            comment_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            comment_btn.color = (0, 0, 0, 1)
            comment_btn.text_size = (self.width * 0.65 - 20, None)
            comment_btn.texture_update()

            stars_btn = RoundedButton(
                text=f"{stars} stars",
                size_hint=(0.3, None),
                height=comment_btn.height
            )
            stars_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            stars_btn.color = (0, 0, 0, 1)

            row = BoxLayout(size_hint_y=None, height=comment_btn.height, spacing=10)
            row.add_widget(stars_btn)
            row.add_widget(comment_btn)
            self.container.add_widget(row)
