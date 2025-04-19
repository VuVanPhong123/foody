from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivymd.uix.button import MDFloatingActionButton,MDIconButton
from frontend.roundButton import RoundedButton
from kivymd.uix.textfield import MDTextField
from kivy.uix.label import Label

import requests
class ChangePasswordScreen(Screen):
    def __init__(self, **kwargs):
        super(ChangePasswordScreen, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        layout = FloatLayout()

        self.old_pass = MDTextField(
            hint_text="Mật khẩu cũ",
            pos_hint={"center_x": 0.5, "center_y": 0.75},
            size_hint_x=0.7,
            password=True
        )
        self.new_pass = MDTextField(
            hint_text="Mật khẩu mới",
            pos_hint={"center_x": 0.5, "center_y": 0.63},
            size_hint_x=0.7,
            password=True
        )
        self.confirm_pass = MDTextField(
            hint_text="Xác nhận mật khẩu",
            pos_hint={"center_x": 0.5, "center_y": 0.51},
            size_hint_x=0.7,
            password=True
        )

        self.eye_old = MDIconButton(
            icon="eye-off",
            md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1),
            pos_hint={"center_x": 0.85, "center_y": 0.75},
            icon_size="20sp",
            on_release=self.toggle_old_password
        )
        layout.add_widget(self.eye_old)

        self.eye_new = MDIconButton(
            icon="eye-off",
            md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1),
            pos_hint={"center_x": 0.85, "center_y": 0.63},
            icon_size="20sp",
            on_release=self.toggle_new_password
        )
        layout.add_widget(self.eye_new)

        self.eye_confirm = MDIconButton(
            icon="eye-off",
            md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1),
            pos_hint={"center_x": 0.85, "center_y": 0.51},
            icon_size="20sp",
            on_release=self.toggle_confirm_password
        )
        layout.add_widget(self.eye_confirm)

        self.notice = Label(
            text="",
            font_size=14,
            color=(1, 0, 0, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.45}
        )


        self.confirm_btn = RoundedButton(
            text="Đổi mật khẩu",
            size_hint=(0.5, 0.07),
            pos_hint={"center_x": 0.5, "center_y": 0.37}
        )
        self.confirm_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
        self.confirm_btn.color=(0, 0, 0, 1)
        self.confirm_btn.bind(on_press=self.change_password)

        self.back_btn = MDFloatingActionButton(
            icon="arrow-left",
            md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1),
            pos_hint={"x": 0.05, "y": 0.05}
        )
        self.back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'settings_owner'))

        layout.add_widget(self.old_pass)
        layout.add_widget(self.new_pass)
        layout.add_widget(self.confirm_pass)
        layout.add_widget(self.notice)
        layout.add_widget(self.confirm_btn)
        layout.add_widget(self.back_btn)

        self.add_widget(layout)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
    def toggle_old_password(self, instance):
        self.old_pass.password = not self.old_pass.password
        instance.icon = "eye" if not self.old_pass.password else "eye-off"

    def toggle_new_password(self, instance):
        self.new_pass.password = not self.new_pass.password
        instance.icon = "eye" if not self.new_pass.password else "eye-off"

    def toggle_confirm_password(self, instance):
        self.confirm_pass.password = not self.confirm_pass.password
        instance.icon = "eye" if not self.confirm_pass.password else "eye-off"

    def change_password(self, instance):
        old = self.old_pass.text.strip()
        new = self.new_pass.text.strip()
        confirm = self.confirm_pass.text.strip()

        if not old or not new or not confirm:
            self.notice.text = "Vui lòng điền đầy đủ thông tin"
            return
        if new != confirm:
            self.notice.text = "Mật khẩu xác nhận không trùng khớp"
            return

        try:
            resp = requests.put("http://localhost:8010/owner/password", json={
                "old_password": old,
                "new_password": new
            })
            if resp.status_code == 200:
                self.notice.text = " Đổi mật khẩu thành công!"
                self.old_pass.text = ""
                self.new_pass.text = ""
                self.confirm_pass.text = ""
            else:
                self.notice.text = resp.json().get("detail", "Lỗi không xác định")
        except Exception as e:
            self.notice.text = f"Lỗi kết nối: {e}"