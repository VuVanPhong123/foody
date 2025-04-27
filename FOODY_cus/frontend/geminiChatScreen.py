import threading, requests
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.spinner import MDSpinner
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from frontend.roundButton import RoundedButton

class GeminiChatScreen(Screen):
    ENDPOINT = "http://localhost:8012/chat"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(245/255, 177/255, 67/255, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.layout = FloatLayout()
        self.add_widget(self.layout)

        # message list
        self.scroll = ScrollView(size_hint=(0.96, 0.7),
                                 pos_hint={"center_x": 0.5, "top": 0.92})
        self.container = BoxLayout(orientation='vertical',
                                   size_hint_y=None,
                                   spacing=10,
                                   padding=10)
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container)
        self.layout.add_widget(self.scroll)

        # input box
        self.question_input = TextInput(
            hint_text="Bạn muốn hỏi gì về menu?",
            size_hint=(0.9, 0.1),
            pos_hint={"center_x": 0.5, "y": 0.15},
            multiline=False
        )
        self.layout.add_widget(self.question_input)

        # send button
        self.ask_btn = Button(
            text="Gửi",
            size_hint=(0.3, 0.07),
            pos_hint={"center_x": 0.5, "y": 0.02},
            background_color=(233/255,150/255,14/255,1),
            color=(0,0,0,1)
        )
        self.ask_btn.bind(on_press=self.send_question)
        self.layout.add_widget(self.ask_btn)

        # spinner (initially hidden)
        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(46, 46),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            line_width=3
        )

        # back button
        self.back_btn = MDFloatingActionButton(
            icon="arrow-left",
            md_bg_color=(233/255,150/255,14/255,1),
            pos_hint={"x":0.02, "y":0.02},
            on_release=self.go_back
        )
        self.layout.add_widget(self.back_btn)

    def update_rect(self, *_):
        self.rect.size, self.rect.pos = self.size, self.pos

    def show_spinner(self):
        if self.spinner.parent is None:
            self.layout.add_widget(self.spinner)

    def hide_spinner(self):
        if self.spinner.parent:
            self.layout.remove_widget(self.spinner)

    def send_question(self, *_):
        question = self.question_input.text.strip()
        if not question:
            return
        self.ask_btn.disabled = True
        self.show_spinner()
        self.question_input.text = ""
        threading.Thread(target=self._ask_worker, args=(question,), daemon=True).start()

    def _ask_worker(self, question):
        try:
            resp = requests.post(self.ENDPOINT, json={"question": question}, timeout=10)
            if resp.status_code == 200:
                answer = resp.json().get("answer", "")
            else:
                answer = " Lỗi từ Gemini hoặc server."
        except Exception as e:
            answer = f" Lỗi kết nối: {e}"
        Clock.schedule_once(lambda dt: self._after_answer(answer), 0)

    def _after_answer(self, answer):
        self.hide_spinner()
        self.ask_btn.disabled = False
        self.add_answer_button(answer)

    def add_answer_button(self, text):
        btn = RoundedButton(
            text=text,
            size_hint=(1, None),
            halign="left",
            valign="middle"
        )
        btn.change_color(233/255,150/255,14/255,1)
        btn.color = (0,0,0,1)
        btn.text_size = (self.scroll.width * 0.9, None)
        btn.font_size = (self.width + self.height) / 2 / 45
        btn.bind(texture_size=lambda i, v: setattr(i, "height", v[1] + 30))
        self.scroll.bind(width=lambda s, w: setattr(btn, "text_size", (w * 0.9, None)))
        self.container.add_widget(btn)
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)

    def go_back(self, *_):
        app = App.get_running_app()
        root = app.root
        root.current = "mainscreen"
        scr = root.get_screen("mainscreen")
        if hasattr(scr, "screen_manager"):
            scr.screen_manager.current = "menu_screen"
