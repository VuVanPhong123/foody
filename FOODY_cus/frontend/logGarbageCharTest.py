import requests
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFloatingActionButton, MDIconButton
from frontend.roundButton import RoundedButton

class LogGarbageCharTest(Screen):
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

        self.login_btn = RoundedButton(text="Đăng nhập (ký tự ẩn)",
                                       size_hint=(.5, .07),
                                       pos_hint={"center_x": .5, "center_y": .35})
        self.login_btn.change_color(233/255,150/255,14/255,1)
        self.login_btn.color = (0, 0, 0, 1)
        self.login_btn.bind(on_press=self.start_login)
        self.layout.add_widget(self.login_btn)

        self.back_btn = MDFloatingActionButton(icon="arrow-left",
                                               pos_hint={"x": .05, "y": .05},
                                               md_bg_color=(233/255,150/255,14/255,1),
                                               on_release=self.go_back)
        self.layout.add_widget(self.back_btn)

    def start_login(self, *_):
        uname = self.username.text.strip() + "\u200B"
        pw = self.password.text.strip()
        try:
            r = requests.post(self.ENDPOINT, json={"username": uname, "password": pw}, timeout=5)
            msg = "Đăng nhập thành công!" if r.status_code == 200 else r.json().get("detail", "Thất bại")
        except Exception as e:
            msg = f"Lỗi: {e}"
        self._popup("Kết quả", msg)

    def _popup(self, title, msg):
        Popup(title=title, content=Label(text=msg),
              size_hint=(None, None), size=(360, 300)).open()

    def toggle_password(self, *_):
        self.password.password = not self.password.password
        self.eye_button.icon = "eye" if not self.password.password else "eye-off"

    def go_back(self, *_):
        self.manager.current = "welcome"

    def update_rect(self, *_):
        self.rect.size = self.size
        self.rect.pos = self.pos