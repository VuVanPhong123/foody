import requests
from frontend.roundButton import RoundedButton
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFloatingActionButton, MDIconButton

class LogScreen(Screen):
    def __init__(self, **kwargs):
        super(LogScreen, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.layout = FloatLayout()
        self.add_widget(self.layout)

        self.layout.add_widget(Image(
            source="images/logo.png",
            size_hint=(None, None),
            size=(400, 400),
            pos_hint={'center_x': 0.5, 'center_y': 0.82}
        ))

        self.username = MDTextField(
            hint_text="Tên tài khoản",
            pos_hint={"center_x": 0.5, "center_y": 0.63},
            size_hint_x=0.7
        )
        self.layout.add_widget(self.username)

        self.password = MDTextField(
            hint_text="Mật khẩu",
            password=True,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size_hint_x=0.7
        )
        self.layout.add_widget(self.password)

        self.eye_button = MDIconButton(
            icon="eye-off",
            pos_hint={"center_x": 0.9, "center_y": 0.5},
            on_release=self.toggle_password,
            md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1)
        )
        self.layout.add_widget(self.eye_button)

        self.error_label = Label(
            text="",
            font_size=15,
            color=(1, 0, 0, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.42}
        )
        self.layout.add_widget(self.error_label)

        self.login_btn = RoundedButton(
            text="Đăng nhập",
            size_hint=(0.5, 0.07),
            pos_hint={"center_x": 0.5, "center_y": 0.35},
        )
        self.login_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
        self.login_btn.color = (0, 0, 0, 1)
        self.login_btn.bind(on_press=self.login)
        self.layout.add_widget(self.login_btn)
        self.signup_btn = RoundedButton(
            text="Bạn chưa có tài khoản?",
            size_hint=(0.5, 0.06),
            pos_hint={"center_x": 0.5, "center_y": 0.26},
            font_size=16
        )
        self.signup_btn.change_color(233/255, 150/255, 14/255, 1)  
        self.signup_btn.color = (0, 0, 0, 1)
        self.signup_btn.bind(on_press=self.go_to_signup)
        self.layout.add_widget(self.signup_btn)
        
        self.back_btn = MDFloatingActionButton(
            icon="arrow-left",
            pos_hint={"x": 0.05, "y": 0.05},
            md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1),
            on_release=self.go_back
        )
        self.layout.add_widget(self.back_btn)
    def go_to_signup(self, instance):
        self.manager.current = "signup"
    def toggle_password(self, instance):
        self.password.password = not self.password.password
        self.eye_button.icon = "eye" if not self.password.password else "eye-off"

    def login(self, instance):
        uname = self.username.text.strip()
        pw = self.password.text.strip()

        if not uname or not pw:
            self.error_label.text = "Vui lòng nhập đầy đủ thông tin"
            return

        try:
            resp = requests.post("http://localhost:8011/login", json={
                "username": uname,
                "password": pw
            })

            if resp.status_code == 200:
                print("Đăng nhập thành công:", uname)
                self.manager.current = "mainscreen"
            else:
                self.error_label.text = resp.json().get("detail", "Đăng nhập thất bại")
        except Exception as e:
            self.error_label.text = f"Lỗi kết nối: {e}"

    def go_back(self, instance):
        self.manager.current = "welcome"

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
