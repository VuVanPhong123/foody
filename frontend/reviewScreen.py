from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivymd.uix.button import MDFloatingActionButton
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import requests

class ReviewScreen(Screen):
    def __init__(self, **kwargs):
        super(ReviewScreen, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.layout = FloatLayout()
        self.stars = []
        self.rating = 0

        for i in range(5):
            star_btn = MDFloatingActionButton(
                icon="star-outline",
                md_bg_color=(1, 1, 1, 1),
                pos_hint={"center_x": 0.22 + i * 0.14, "center_y": 0.7},
                icon_color=(0, 0, 0, 1)
            )
            star_btn.index = i + 1
            star_btn.bind(on_press=self.update_stars)
            self.layout.add_widget(star_btn)
            self.stars.append(star_btn)

        self.comment_box = TextInput(
            hint_text="Viết đánh giá của bạn...",
            size_hint=(0.8, 0.3),
            pos_hint={"center_x": 0.5, "center_y": 0.45},
            multiline=True
        )
        self.layout.add_widget(self.comment_box)

        clear_btn = Button(
            text="Xóa đánh giá",
            size_hint=(0.4, 0.1),
            pos_hint={"x": 0.05, "y": 0.18},
            background_color=(0.7, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        clear_btn.bind(on_press=self.clear_review)
        self.layout.add_widget(clear_btn)
        confirm_btn = Button(
            text="Xác nhận",
            size_hint=(0.4, 0.1),
            pos_hint={"x": 0.55, "y": 0.18},
            background_color=(0.2, 0.6, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        confirm_btn.bind(on_press=self.submit_review)
        self.layout.add_widget(confirm_btn)

        self.back_button = MDFloatingActionButton(
            icon="arrow-left",
            md_bg_color=(233/255, 150/255, 14/255, 1),
            pos_hint={'center_x': 0.18, 'center_y': 0.1}
        )
        self.back_button.bind(on_press=self.go_back)
        self.add_widget(self.back_button)

        self.add_widget(self.layout)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
    def go_back(self, instance):
        self.manager.current = "settings"

    def update_stars(self, instance):
        self.rating = instance.index
        for star in self.stars:
            if star.index <= self.rating:
                star.icon = "star"
                star.md_bg_color = (233 / 255, 150 / 255, 14 / 255, 1)
            else:
                star.icon = "star-outline"
                star.md_bg_color = (1, 1, 1, 1)

    def clear_review(self, instance):
        self.rating = 0
        self.comment_box.text = ""
        for star in self.stars:
            star.icon = "star-outline"
            star.md_bg_color = (1, 1, 1, 1)
    def show_popup(self, message):
        content = Label(text=message)
        popup = Popup(
            title="Thông báo",
            content=content,
            size_hint=(None, None),
            size=(300, 150),
            auto_dismiss=True
        )
        popup.open()
    def submit_review(self, instance):
        if self.rating == 0 and self.comment_box.text.strip() == "":
            print("Empty review")
            return
        payload = {
            "stars": self.rating,
            "comment": self.comment_box.text.strip()
        }
        try:
            response = requests.post("http://localhost:8008/review", json=payload)
            print(response.json())
            if response.status_code == 200:
                self.show_popup("Gửi thành công") 
                self.comment_box.text = ""
                for star in self.stars:
                    star.icon = "star-outline"
                    star.md_bg_color = (1, 1, 1, 1)
            else:
                self.show_popup("Lỗi khi gửi đánh giá.")
        except Exception as e:
            print("Failed to submit review:", e)
        
