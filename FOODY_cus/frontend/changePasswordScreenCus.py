import requests
from frontend.roundButton import RoundedButton
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFloatingActionButton, MDIconButton

class ChangePasswordScreen(Screen):
    def __init__(self, **kwargs):
        super(ChangePasswordScreen, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245/255, 177/255, 67/255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.layout = FloatLayout()
        self.add_widget(self.layout)

        # Username (optional display only)
        self.username = ""  # <- should be set after login
        self.user_label = Label(
            text="",
            font_size=18,
            color=(0, 0, 0, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.78}
        )
        self.layout.add_widget(self.user_label)

        # Old password
        self.old_pass = MDTextField(
            hint_text="Mật khẩu cũ",
            password=True,
            pos_hint={"center_x": 0.5, "center_y": 0.65},
            size_hint_x=0.7
        )
        self.layout.add_widget(self.old_pass)

        # New password
        self.new_pass = MDTextField(
            hint_text="Mật khẩu mới",
            password=True,
            pos_hint={"center_x": 0.5, "center_y": 0.53},
            size_hint_x=0.7
        )
        self.layout.add_widget(self.new_pass)

        # Confirm password
        self.confirm_pass = MDTextField(
            hint_text="Xác nhận mật khẩu",
            password=True,
            pos_hint={"center_x": 0.5, "center_y": 0.41},
            size_hint_x=0.7
        )
        self.layout.add_widget(self.confirm_pass)

        # Eye icons
        self.eye1 = MDIconButton(
            icon="eye-off", pos_hint={"center_x": 0.85, "center_y": 0.65},
            on_release=self.toggle_old)
        self.eye2 = MDIconButton(
            icon="eye-off", pos_hint={"center_x": 0.85, "center_y": 0.53},
            on_release=self.toggle_new)
        self.eye3 = MDIconButton(
            icon="eye-off", pos_hint={"center_x": 0.85, "center_y": 0.41},
            on_release=self.toggle_confirm)
        self.layout.add_widget(self.eye1)
        self.layout.add_widget(self.eye2)
        self.layout.add_widget(self.eye3)

        # Error/Success label
        self.status = Label(
            text="",
            font_size=14,
            color=(1, 0, 0, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.34}
        )
        self.layout.add_widget(self.status)

        # Change button
        self.confirm_btn = RoundedButton(
            text="Đổi mật khẩu",
            size_hint=(0.5, 0.07),
            pos_hint={"center_x": 0.5, "center_y": 0.26}
        )
        self.confirm_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
        self.confirm_btn.bind(on_press=self.change_password)
        self.layout.add_widget(self.confirm_btn)

        # Back button
        self.back_btn = MDFloatingActionButton(
            icon="arrow-left",
            pos_hint={"x": 0.05, "y": 0.05},
            md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1),
            on_release=self.go_back
        )
        self.layout.add_widget(self.back_btn)

    def set_username(self, uname):
        self.username = uname.strip()
        self.user_label.text = f"Đổi mật khẩu cho: {self.username}"


    def toggle_old(self, instance):
        self.old_pass.password = not self.old_pass.password
        instance.icon = "eye" if not self.old_pass.password else "eye-off"

    def toggle_new(self, instance):
        self.new_pass.password = not self.new_pass.password
        instance.icon = "eye" if not self.new_pass.password else "eye-off"

    def toggle_confirm(self, instance):
        self.confirm_pass.password = not self.confirm_pass.password
        instance.icon = "eye" if not self.confirm_pass.password else "eye-off"

    def change_password(self, instance):
        old = self.old_pass.text.strip()
        new = self.new_pass.text.strip()
        confirm = self.confirm_pass.text.strip()

        if not old or not new or not confirm:
            self.status.text = "Vui lòng điền đầy đủ thông tin"
            return
        if new != confirm:
            self.status.text = "Xác nhận mật khẩu không khớp"
            return

        try:
            resp = requests.put("http://localhost:8011/change_pass", json={
                "username": self.username,
                "old_password": old,
                "new_password": new
            })
            if resp.status_code == 200:
                self.status.color = (0, 0.5, 0, 1)
                self.status.text = " Đổi mật khẩu thành công"
                self.old_pass.text = self.new_pass.text = self.confirm_pass.text = ""
            else:
                self.status.color = (1, 0, 0, 1)
                self.status.text = resp.json().get("detail", "Đổi mật khẩu thất bại")
        except Exception as e:
            self.status.text = f"Lỗi kết nối: {e}"

    def go_back(self, instance):
        self.manager.current = "settings"

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
