import requests
import threading

from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

from kivymd.app import MDApp
from kivymd.uix.button import MDFloatingActionButton, MDIconButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.textfield import MDTextField

from frontend.roundButton import RoundedButton


class LogScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.add_widget(Image(source="images/logo.png",
                              size_hint=(None, None), size=(400, 400),
                              pos_hint={'center_x': .5, 'center_y': .82}))

        self.add_widget(Label(text="Mật khẩu: ", font_size=20,
                              size_hint=(None, None), size=(150, 50),
                              pos_hint={'center_x': .2, 'top': .58},
                              color=(0, 0, 0, 1)))

        self.Password = MDTextField(hint_text='mật khẩu', multiline=False,
                                    pos_hint={'x': .32, 'y': .51},
                                    size_hint_x=.48, password=True)
        self.add_widget(self.Password)

        self.eye_button = MDIconButton(icon="eye-off",
                                       md_bg_color=(233/255,150/255,14/255,1),
                                       pos_hint={'center_x': .87, 'center_y': .56},
                                       icon_size="15sp",
                                       on_release=self.toggle_password)
        self.add_widget(self.eye_button)

        self.button = MDFloatingActionButton(icon="arrow-left",
                                             md_bg_color=(233/255,150/255,14/255,1),
                                             pos_hint={'center_x': .18, 'center_y': .1},
                                             on_press=self.go_back)
        self.add_widget(self.button)

        self.login_btn = RoundedButton(text="Đăng Nhập",
                                       size_hint=(.45, .07), font_size=25,
                                       pos_hint={"center_x": .5, "center_y": .4})
        self.login_btn.change_color(233/255,150/255,14/255,1)
        self.login_btn.color = (0, 0, 0, 1)
        self.login_btn.bind(on_press=self.start_login)
        self.add_widget(self.login_btn)

        # widgets that appear/disappear
        self.error_label = None
        self.spinner     = None

    def go_back(self, *_):
        self.manager.current = 'welcome'

    def show_error(self, msg):
        if self.error_label:
            self.remove_widget(self.error_label)
        self.error_label = Label(text=msg, font_size=15,
                                 size_hint=(None, None), size=(150, 50),
                                 color=(1, 0, 0, 1),
                                 pos_hint={'center_x': .5, 'top': .35})
        self.add_widget(self.error_label)

    def show_spinner(self):
        if not self.spinner:
            self.spinner = MDSpinner(size_hint=(None, None), size=(46, 46),
                                     pos_hint={'center_x': .5, 'y': .05},
                                     line_width=3, color=(1, 1, 1, 1))
            self.add_widget(self.spinner)

    def hide_spinner(self):
        if self.spinner:
            self.remove_widget(self.spinner)
            self.spinner = None

    def toggle_password(self, *_):
        self.Password.password = not self.Password.password
        self.eye_button.icon = "eye" if not self.Password.password else "eye-off"

    def start_login(self, *_):
        pwd = self.Password.text.strip()
        if not pwd:
            self.show_error("Vui lòng nhập mật khẩu")
            return
        if self.error_label:
            self.remove_widget(self.error_label)
            self.error_label = None
        self.show_spinner()

        threading.Thread(target=self._login_worker, args=(pwd,), daemon=True).start()

    def _login_worker(self, pwd):
        try:
            resp = requests.post("http://localhost:8010/owner/login",
                                 json={"password": pwd}, timeout=5)
            ok = resp.status_code == 200
        except Exception as e:
            ok, error_msg = False, f"Lỗi kết nối: {e}"
        else:
            error_msg = None if ok else "Mật khẩu sai!"

        Clock.schedule_once(lambda dt: self._after_login(ok, error_msg))

    def _after_login(self, ok, error_msg):
        self.hide_spinner()
        if ok:
            self.manager.current = 'mainscreen'
        else:
            self.show_error(error_msg)

    def update_rect(self, *_):
        self.rect.size = self.size
        self.rect.pos = self.pos


class _Demo(MDApp):
    def build(self):
        return LogScreen()


if __name__ == '__main__':
    _Demo().run()
