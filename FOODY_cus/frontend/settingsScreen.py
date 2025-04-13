# frontend/settingsScreen.py

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from frontend.roundButton import RoundedButton
from kivy.uix.image import Image
from kivymd.uix.button import MDFloatingActionButton

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245/255, 177/255, 67/255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        layout = FloatLayout()

        btn_labels = ["Đổi mật khẩu", "Liên hệ", "Phản hồi", "Thoát"]

        for i, label in enumerate(btn_labels):
            btn = RoundedButton(
                text=label,
                size_hint=(0.6, 0.1),
                pos_hint={"center_x": 0.5, "center_y": 0.75 - i * 0.15}
            )
            btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            btn.color=(0,0,0,1)
            layout.add_widget(btn)

        self.button = MDFloatingActionButton(
            icon="arrow-left",
            md_bg_color=(233/255, 150/255, 14/255, 1),
            pos_hint={'center_x': 0.18, 'center_y': 0.1}
        )
        self.button.bind(on_press=self.go_back)
        self.add_widget(self.button)
        self.add_widget(layout)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def go_back(self, instance):
        self.manager.current = "mainscreen"
