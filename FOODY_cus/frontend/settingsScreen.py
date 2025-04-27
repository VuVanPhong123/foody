from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.spinner import MDSpinner
from frontend.roundButton import RoundedButton


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self._busy = None
        layout = FloatLayout()

        for i, text in enumerate(["Đổi mật khẩu", "Liên hệ", "Phản hồi", "Thoát"]):
            btn = RoundedButton(
                text=text,
                size_hint=(.6, .1),
                pos_hint={"center_x": .5, "center_y": .75 - i * .15},
            )
            btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            btn.color = (0, 0, 0, 1)

            if text == "Liên hệ":
                btn.bind(on_press=self.go_to_chat)
            elif text == "Đổi mật khẩu":
                btn.bind(on_press=lambda *_: setattr(self.manager, "current", "changepass"))
            elif text == "Phản hồi":
                btn.bind(on_press=lambda *_: setattr(self.manager, "current", "review"))
            elif text == "Thoát":
                btn.bind(on_press=self.quit_app)

            layout.add_widget(btn)

        back = MDFloatingActionButton(
            icon="arrow-left",
            md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1),
            pos_hint={"center_x": .18, "center_y": .1},
            on_release=lambda *_: setattr(self.manager, "current", "mainscreen"),
        )
        self.add_widget(layout)
        self.add_widget(back)

    def _show_busy(self):
        if self._busy is None:
            self._busy = MDSpinner(
                size_hint=(None, None), size=(46, 46), line_width=3,
                pos_hint={"center_x": .5, "center_y": .15}
            )
            self._busy.active = True          
            self.add_widget(self._busy)

    def _hide_busy(self, *_):
        if self._busy:
            self._busy.active = False
            self.remove_widget(self._busy)
            self._busy = None

    def go_to_chat(self, *_):
        self._show_busy()
        Clock.schedule_once(self._open_chat, .15)

    def _open_chat(self, *_):
        self.manager.current = "chat"
        self._hide_busy()

    def quit_app(self, *_):
        import sys; sys.exit()

    def update_rect(self, *_):
        self.rect.size = self.size
        self.rect.pos = self.pos
