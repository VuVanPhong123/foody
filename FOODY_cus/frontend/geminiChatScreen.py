from audioop import add
import threading, requests, json
from datetime import datetime
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.spinner import MDSpinner
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from frontend.roundButton import RoundedButton
import uuid
import re

class ChatHistory:
    def __init__(self):
        self._history = []

    def add_message(self, message):
        if len(self._history) > 10:
            self._history.pop(0)
        self._history.append(message)

    def get_history(self):
        return self._history

history_chat = ChatHistory()

class GeminiChatScreen(Screen):
    ENDPOINT = "http://localhost:8012/chat"
    HISTORY_ENDPOINT = "http://localhost:8012/chat/history/recent"
    END_SESSION_ENDPOINT = "http://localhost:8012/chat/end"
    START_SESSION_ENDPOINT = "http://localhost:8012/chat/start"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session_id = None

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

        # RAG toggle
        rag_box = BoxLayout(
            orientation='horizontal',
            size_hint=(0.5, 0.05),
            pos_hint={"center_x": 0.3, "y": 0.06}
        )

        self.rag_checkbox = CheckBox(active=True)
        rag_box.add_widget(self.rag_checkbox)

        self.layout.add_widget(rag_box)

        # send button
        self.ask_btn = Button(
            text="Gửi",
            size_hint=(0.3, 0.07),
            pos_hint={"center_x": 0.75, "y": 0.02},
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

        # clear history button
        self.clear_btn = MDFloatingActionButton(
            icon="trash-can",
            md_bg_color=(233/255,150/255,14/255,1),
            pos_hint={"right":0.98, "y":0.02},
            on_release=self.clear_history
        )
        self.layout.add_widget(self.clear_btn)

    def on_enter(self, *args):
        # Start a new session when entering the screen
        self.start_new_session()
        # Load chat history
        self.load_chat_history()

    def on_leave(self, *args):
        # End session when leaving the screen
        if self.session_id:
            self.end_session()

    def update_rect(self, *_):
        self.rect.size, self.rect.pos = self.size, self.pos

    def show_spinner(self):
        if self.spinner.parent is None:
            self.layout.add_widget(self.spinner)

    def hide_spinner(self):
        if self.spinner.parent:
            self.layout.remove_widget(self.spinner)

    def load_chat_history(self):
        self.show_spinner()
        self.container.clear_widgets()
        threading.Thread(target=self._load_history_worker, daemon=True).start()

    def remove_user_assistant_lines(self, text:str):
         # Pattern regex để khớp các dòng chứa "user:" hoặc "assistant:"
         pattern = r'.*(user:|assistant:).*'

         # Tách văn bản thành các dòng
         lines = text.splitlines()

         # Tìm dòng đầu tiên không khớp với pattern
         for line in lines:
             print(line)
             if not re.match(pattern, line):
                 return line

         return ""  #
    def _load_history_worker(self):
        try:
            resp = requests.get(self.HISTORY_ENDPOINT, timeout=10)
            if resp.status_code == 200:
                history = resp.json()
                for chat in reversed(history):
                    chat_user = self.remove_user_assistant_lines(chat["question"])
                    history_chat.add_message(chat_user + chat["answer"]) # Show oldest first
                    Clock.schedule_once(lambda dt, q=chat_user:
                                       self.add_question_button(q), 0)
                    Clock.schedule_once(lambda dt, a=chat["answer"]:
                                       self.add_answer_button(a), 0)
        except Exception as e:
            error_msg = str(e)  # Capture the error message
            Clock.schedule_once(lambda dt, msg=error_msg: self.add_answer_button(f"Không thể tải lịch sử: {msg}"), 0)
        Clock.schedule_once(lambda dt: self.hide_spinner(), 0)

    def clear_history(self, *args):
        self.show_spinner()
        threading.Thread(target=self._clear_history_worker, daemon=True).start()

    def _clear_history_worker(self):
        try:
            resp = requests.delete("http://localhost:8012/chat/history", timeout=10)
            Clock.schedule_once(lambda dt: self.load_chat_history(), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.add_answer_button(f"Không thể xóa lịch sử: {e}"), 0)
            Clock.schedule_once(lambda dt: self.hide_spinner(), 0)

    def send_question(self, *_):
        question = self.question_input.text.strip()
        if not question:
            return
        self.ask_btn.disabled = True
        self.show_spinner()
        self.add_question_button(question)
        self.question_input.text = ""
        threading.Thread(target=self._ask_worker, args=(question,), daemon=True).start()

    def _ask_worker(self, question):
        try:
            # Get RAG toggle state
            use_rag = self.rag_checkbox.active

            resp = requests.post(
                self.ENDPOINT,
                json={
                    "question": question + "\n\n" + "\n".join(history_chat.get_history()),
                    "session_id": self.session_id,
                    "use_rag": use_rag
                },
                timeout=15  # Longer timeout for RAG processing
            )
            if resp.status_code == 200:
                result = resp.json()
                answer = result.get("answer", "")
                history_chat.add_message('user: ' + question + '\n' + 'assistant: ' + answer)
                # Update session ID in case a new one was created
                if result.get("session_id"):
                    self.session_id = result["session_id"]
            else:
                print(resp.json())
                answer = " Lỗi từ Gemini hoặc server."
        except Exception as e:
            answer = f" Lỗi kết nối: {e}"
        Clock.schedule_once(lambda dt: self._after_answer(answer), 0)

    def _after_answer(self, answer):
        self.hide_spinner()
        self.ask_btn.disabled = False
        self.add_answer_button(answer)


    def add_question_button(self, text):

        btn = RoundedButton(
            text=text,
            size_hint=(0.8, None),
            halign="left",
            valign="middle",
            pos_hint={"right": 1}
        )
        btn.change_color(100/255, 200/255, 100/255, 1)
        btn.color = (0, 0, 0, 1)
        btn.text_size = (self.scroll.width * 0.7, None)
        btn.font_size = (self.width + self.height) / 2 / 45
        btn.bind(texture_size=lambda i, v: setattr(i, "height", v[1] + 30))
        self.container.add_widget(btn)
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)

    def add_answer_button(self, text):
        btn = RoundedButton(
            text=text,
            size_hint=(0.8, None),
            halign="left",
            valign="middle",
            pos_hint={"x": 0}
        )
        btn.change_color(233/255, 150/255, 14/255, 1)
        btn.color = (0, 0, 0, 1)
        btn.text_size = (self.scroll.width * 0.7, None)
        btn.font_size = (self.width + self.height) / 2 / 45
        btn.bind(texture_size=lambda i, v: setattr(i, "height", v[1] + 30))
        self.scroll.bind(width=lambda s, w: setattr(btn, "text_size", (w * 0.7, None)))
        self.container.add_widget(btn)
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)

    def go_back(self, *_):
        app = App.get_running_app()
        root = app.root
        root.current = "mainscreen"
        scr = root.get_screen("mainscreen")
        if hasattr(scr, "screen_manager"):
            scr.screen_manager.current = "menu_screen"

    def start_new_session(self):
        try:
            resp = requests.post(self.START_SESSION_ENDPOINT, timeout=10)
            if resp.status_code == 200:
                self.session_id = resp.json().get("session_id")
        except Exception as e:
            print(f"Error starting new session: {e}")

    def end_session(self):
        try:
            requests.post(
                self.END_SESSION_ENDPOINT,
                json={"session_id": self.session_id},
                timeout=10
            )
        except Exception as e:
            print(f"Error ending session: {e}")
        self.session_id = None
