from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivymd.uix.button import MDFloatingActionButton
from kivy.graphics import Color, Rectangle
from frontend.roundButton import RoundedButton
from kivy.clock import Clock
import requests

class ChatScreenCus(Screen):
    def __init__(self, **kwargs):
        super(ChatScreenCus, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        main_layout = BoxLayout(orientation='vertical')

        top_bar = BoxLayout(size_hint=(1, 0.15), padding=10)
        back_btn = MDFloatingActionButton(
            icon="arrow-left",
            md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1),
            icon_color=(0, 0, 0, 1),
            size_hint=(None, None),
            size=("20dp", "20dp")
        )
        back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(back_btn)

        self.scroll = ScrollView(size_hint=(1, 0.82))
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container)

        input_row = BoxLayout(size_hint=(1, 0.1), spacing=10, padding=10)
        self.input_text = TextInput(hint_text="Nhập tin nhắn", size_hint=(0.8, 1), multiline=False)
        send_btn = Button(text="Gửi", size_hint=(0.2, 1), background_color=(233 / 255, 150 / 255, 14 / 255, 1))
        send_btn.bind(on_press=self.send_message)
        input_row.add_widget(self.input_text)
        input_row.add_widget(send_btn)

        main_layout.add_widget(top_bar)
        main_layout.add_widget(self.scroll)
        main_layout.add_widget(input_row)
        self.add_widget(main_layout)
        self.refresh_event = None
        self.load_messages()

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def go_back(self, instance):
        self.manager.current = "settings_owner"

    def on_pre_enter(self, *args):
        self.load_messages()
        self.refresh_event = Clock.schedule_interval(lambda dt: self.load_messages(), 10)
    def on_leave(self, *args):
        if self.refresh_event:
            self.refresh_event.cancel()
            self.refresh_event = None
    def load_messages(self):
        self.container.clear_widgets()
        try:
            resp = requests.get("http://localhost:8009/chat")
            messages = resp.json()
        except Exception as e:
            self.container.add_widget(RoundedButton(
                text=f"Lỗi tải tin nhắn: {e}",
                size_hint=(None, None),
                width=320,
                pos_hint={"x": 0}
            ))
            return

        for msg in messages:
            sender, content, color = "", "", ()

            if msg.get("owner"):
                sender = "Me"
                content = msg["owner"]
            elif msg.get("customer"):
                sender = "Customer"
                content = msg["customer"]

            full_text = f"{sender}:\n{content}"

            msg_btn = RoundedButton(
                text=full_text,
                size_hint=(None, None),
                width=320,
                halign="left",
                valign="middle",
                text_size=(280, None)
            )
            if sender=="Me":
                msg_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            else:
                msg_btn.change_color(0.9, 0.4, 0.1, 1)
            msg_btn.color = (0, 0, 0, 1)
            msg_btn.bind(texture_size=lambda b, ts: setattr(b, 'height', ts[1] + 20))
            msg_btn.pos_hint = {"x": 0}
            self.container.add_widget(msg_btn)
            Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)

    def send_message(self, instance):
        text = self.input_text.text.strip()
        if not text:
            return
        payload = {
            "sender": "owner",
            "message": text
        }

        try:
            resp = requests.post("http://localhost:8009/chat", json=payload)
            if resp.status_code == 200:
                self.input_text.text = ""
                self.load_messages()
        except Exception as e:
            print("Send failed:", e)
