import requests
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivymd.uix.button import MDFloatingActionButton
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from frontend.roundButton import RoundedButton

class GeminiChatScreen(Screen):
    def __init__(self, **kwargs):
        super(GeminiChatScreen, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.layout = FloatLayout()
        self.add_widget(self.layout)
        self.scroll = ScrollView(
            size_hint=(0.96, 0.7),
            pos_hint={"center_x": 0.5, "top": 0.92}
        )
        self.container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=10,
            padding=10
        )
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container)
        self.layout.add_widget(self.scroll)

        # Input for question
        self.question_input = TextInput(
            hint_text="Bạn muốn hỏi gì về menu?",
            size_hint=(0.9, 0.1),
            pos_hint={"center_x": 0.5, "y": 0.15},
            multiline=False
        )
        self.layout.add_widget(self.question_input)

        self.ask_btn = Button(
            text="Gửi",
            size_hint=(0.3, 0.07),
            pos_hint={"center_x": 0.5, "y": 0.02},
            background_color=(233 / 255, 150 / 255, 14 / 255, 1),
            color=(0, 0, 0, 1)
        )
        self.ask_btn.bind(on_press=self.send_question)
        self.layout.add_widget(self.ask_btn)

        # Back button
        self.back_btn = MDFloatingActionButton(
            icon="arrow-left",
            md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1),
            pos_hint={"x": 0.02, "y": 0.02},
            on_release=self.go_back
        )
        self.layout.add_widget(self.back_btn)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def send_question(self, instance):
        question = self.question_input.text.strip()
        if not question:
            return

        try:
            resp = requests.post("http://localhost:8012/chat", json={"question": question})
            if resp.status_code == 200:
                answer = resp.json().get("answer", "")
                self.add_answer_button(answer)
            else:
                self.add_answer_button(" Lỗi từ Gemini hoặc server.")
        except Exception as e:
            self.add_answer_button(f" Lỗi kết nối: {e}")

        self.question_input.text = ""

    def add_answer_button(self, text):
        btn = RoundedButton(
            text=text,
            size_hint=(1, None),
            halign="left",
            valign="middle"
        )
        btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
        btn.color=(0,0,0,1)
        btn.text_size = (self.scroll.width * 0.9, None)
        avg_size = (self.width + self.height) / 2
        btn.font_size = avg_size / 45
        def update_height(instance, value):
            instance.height = instance.texture_size[1] + 30  
        btn.bind(texture_size=update_height)

        self.scroll.bind(width=lambda scroll, w: setattr(btn, "text_size", (w * 0.9, None)))

        self.container.add_widget(btn)


    def go_back(self, instance):
        self.manager.current = "menu_screen"
