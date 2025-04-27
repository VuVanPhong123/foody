# frontend/logScreencus.py
import threading, requests
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFloatingActionButton, MDIconButton
from kivymd.uix.spinner import MDSpinner

from frontend.roundButton import RoundedButton


class LogScreen(Screen):
    ENDPOINT = "http://localhost:8011/login"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.layout = FloatLayout()
        self.add_widget(self.layout)

        self.layout.add_widget(Image(source="images/logo.png",
                                     size_hint=(None, None), size=(400, 400),
                                     pos_hint={'center_x': .5, 'center_y': .82}))

        self.username = MDTextField(hint_text="Tên tài khoản",
                                    pos_hint={"center_x": .5, "center_y": .63},
                                    size_hint_x=.7)
        self.layout.add_widget(self.username)

        self.password = MDTextField(hint_text="Mật khẩu", password=True,
                                    pos_hint={"center_x": .5, "center_y": .5},
                                    size_hint_x=.7)
        self.layout.add_widget(self.password)

        self.eye_button = MDIconButton(icon="eye-off",
                                       pos_hint={"center_x": .9, "center_y": .5},
                                       on_release=self.toggle_password,
                                       md_bg_color=(233/255,150/255,14/255,1))
        self.layout.add_widget(self.eye_button)

        self.error_label = Label(text="", font_size=15,
                                 color=(1, 0, 0, 1),
                                 pos_hint={"center_x": .5, "center_y": .42})
        self.layout.add_widget(self.error_label)

        self.login_btn = RoundedButton(text="Đăng nhập",
                                       size_hint=(.5, .07),
                                       pos_hint={"center_x": .5, "center_y": .35})
        self.login_btn.change_color(233/255,150/255,14/255,1)
        self.login_btn.color = (0, 0, 0, 1)
        self.login_btn.bind(on_press=self.start_login)
        self.layout.add_widget(self.login_btn)

        self.signup_btn = RoundedButton(text="Bạn chưa có tài khoản?",
                                        size_hint=(.5, .06),
                                        pos_hint={"center_x": .5, "center_y": .26},
                                        font_size=16)
        self.signup_btn.change_color(233/255,150/255,14/255,1)
        self.signup_btn.color = (0, 0, 0, 1)
        self.signup_btn.bind(on_press=self.go_to_signup)
        self.layout.add_widget(self.signup_btn)

        self.back_btn = MDFloatingActionButton(icon="arrow-left",
                                               pos_hint={"x": .05, "y": .05},
                                               md_bg_color=(233/255,150/255,14/255,1),
                                               on_release=self.go_back)
        self.layout.add_widget(self.back_btn)

        self.spinner = None

    def show_spinner(self):
        if self.spinner is None:
            self.spinner = MDSpinner(size_hint=(None, None), size=(46, 46),
                                     line_width=3, color=(1, 1, 1, 1),
                                     pos_hint={'center_x': .5, 'y': .05})
            self.layout.add_widget(self.spinner)

    def hide_spinner(self):
        if self.spinner:
            self.layout.remove_widget(self.spinner)
            self.spinner = None

    def toggle_password(self, *_):
        self.password.password = not self.password.password
        self.eye_button.icon = "eye" if not self.password.password else "eye-off"

    def go_back(self, *_):
        self.manager.current = "welcome"

    def go_to_signup(self, *_):
        self.manager.current = "signup"
    def start_login(self, *_):
        uname, pw = self.username.text.strip(), self.password.text.strip()
        if not uname or not pw:
            self.error_label.text = "Vui lòng nhập đầy đủ thông tin"
            return

        self.error_label.text = ""
        self.show_spinner()
        threading.Thread(target=self._login_worker,
                         args=(uname, pw), daemon=True).start()

    def _login_worker(self, uname, pw):
        try:
            resp = requests.post(self.ENDPOINT,
                                 json={"username": uname, "password": pw},
                                 timeout=5)
            ok = resp.status_code == 200
            detail = "" if ok else resp.json().get("detail", "Đăng nhập thất bại")
        except Exception as e:
            ok, detail = False, f"Lỗi kết nối: {e}"

        Clock.schedule_once(lambda dt: self._after_login(ok, detail))

    def _after_login(self, ok, detail):
        self.hide_spinner()
        if ok:
            self.manager.current = "mainscreen"
        else:
            self.error_label.text = detail

    def update_rect(self, *_):
        self.rect.size = self.size
        self.rect.pos  = self.pos
