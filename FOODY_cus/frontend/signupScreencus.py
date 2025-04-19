import requests
from frontend.roundButton import RoundedButton
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFloatingActionButton, MDIconButton

class SignUpScreen(Screen):
    def __init__(self, **kwargs):
        super(SignUpScreen, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245/255, 177/255, 67/255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.layout = FloatLayout()
        self.add_widget(self.layout)

        self.layout.add_widget(Image(
            source="images/logo.png",
            size_hint=(None, None),
            size=(400, 400),
            pos_hint={"center_x": 0.5, "center_y": 0.82}
        ))

        # Username field
        self.username = MDTextField(
            hint_text="Tên tài khoản",
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            size_hint_x=0.7
        )
        self.layout.add_widget(self.username)

        # Password field
        self.password = MDTextField(
            hint_text="Mật khẩu",
            password=True,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size_hint_x=0.7
        )
        self.layout.add_widget(self.password)

        # Confirm password field
        self.confirm = MDTextField(
            hint_text="Xác nhận mật khẩu",
            password=True,
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            size_hint_x=0.7
        )
        self.layout.add_widget(self.confirm)

        # Eye icons
        self.eye1 = MDIconButton(
            icon="eye-off",
            pos_hint={"center_x": 0.85, "center_y": 0.5},
            md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1),
            on_release=self.toggle_pass
        )
        self.eye2 = MDIconButton(
            icon="eye-off",
            pos_hint={"center_x": 0.85, "center_y": 0.4},
            md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1),
            on_release=self.toggle_confirm
        )
        self.layout.add_widget(self.eye1)
        self.layout.add_widget(self.eye2)

        # Notification label
        self.error_label = Label(
            text="",
            font_size=14,
            color=(1, 0, 0, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.34}
        )
        self.layout.add_widget(self.error_label)

        # Register button
        self.register_btn = RoundedButton(
            text="Đăng ký",
            size_hint=(0.5, 0.07),
            pos_hint={"center_x": 0.5, "center_y": 0.27},
        )
        self.register_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
        self.register_btn.color = (0, 0, 0, 1)
        self.register_btn.bind(on_press=self.register)
        self.layout.add_widget(self.register_btn)

        # Back button
        self.back_btn = MDFloatingActionButton(
            icon="arrow-left",
            pos_hint={"x": 0.05, "y": 0.05},
            md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1),
            on_release=self.go_back
        )
        self.layout.add_widget(self.back_btn)

    def toggle_pass(self, instance):
        self.password.password = not self.password.password
        self.eye1.icon = "eye" if not self.password.password else "eye-off"

    def toggle_confirm(self, instance):
        self.confirm.password = not self.confirm.password
        self.eye2.icon = "eye" if not self.confirm.password else "eye-off"

    def register(self, instance):
        uname = self.username.text.strip()
        pw = self.password.text.strip()
        cf = self.confirm.text.strip()

        if not uname or not pw or not cf:
            self.error_label.text = "Vui lòng nhập đầy đủ thông tin"
            return
        if pw != cf:
            self.error_label.text = "Mật khẩu xác nhận không trùng khớp"
            return

        try:
            resp = requests.post("http://localhost:8011/register", json={
                "username": uname,
                "password": pw
            })
            if resp.status_code == 200:
                self.error_label.text = " Đăng ký thành công!"
                self.username.text = ""
                self.password.text = ""
                self.confirm.text = ""
            else:
                self.error_label.text = resp.json().get("detail", "Đăng ký thất bại")
        except Exception as e:
            self.error_label.text = f"Lỗi kết nối: {e}"

    def go_back(self, instance):
        self.manager.current = "log"

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
