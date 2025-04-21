from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivymd.uix.button import MDFloatingActionButton
from kivy.graphics import Color, Rectangle
from frontend.roundButton import RoundedButton
from kivy.clock import Clock, mainthread
import requests
from threading import Thread




class Converstaion:
    
    def __init__(self):
        self.messages = []

class AIChatScreen(Screen):
    def __init__(self, **kwargs):
        super(AIChatScreen, self).__init__(**kwargs)

        # Set background color
        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)  # Orange background
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        # Main layout
        main_layout = BoxLayout(orientation='vertical')

        # Top bar with back button
        top_bar = BoxLayout(size_hint=(1, 0.1), padding=10)

        # Scrollable message area
        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container)

        # Input area
        input_row = BoxLayout(size_hint=(1, 0.1), spacing=10, padding=10)
        self.input_text = TextInput(
            hint_text="Nhập tin nhắn của bạn...",
            size_hint=(0.8, 1),
            multiline=False,
            font_size=14
        )
        self.input_text.bind(on_text_validate=self.send_message)  # Send on Enter key
        
        send_btn = Button(
            text="Gửi",
            size_hint=(0.2, 1),
            background_color=(233 / 255, 150 / 255, 14 / 255, 1)
        )
        send_btn.bind(on_press=self.send_message)
        
        input_row.add_widget(self.input_text)
        input_row.add_widget(send_btn)

        # Add all components to main layout
        main_layout.add_widget(top_bar)
        main_layout.add_widget(self.scroll)
        main_layout.add_widget(input_row)
        
        self.add_widget(main_layout)
        self.conversation = []
        
        # Add welcome message
        Clock.schedule_once(lambda dt: self.add_assistant_message(
            "Xin chào! Tôi là trợ lý AI của Foody. Bạn cần giúp gì không?"
        ), 0.5)

    def update_rect(self, *args):
        """Update background rectangle size when window resizes"""
        self.rect.size = self.size
        self.rect.pos = self.pos


    def add_user_message(self, text):
        """Add a user message to the chat"""
        self.add_message_bubble(text, is_user=True)
        self.conversation.append({"role": "user", "content": text})
    @mainthread
    def add_assistant_message(self, text):
        """Add an assistant message to the chat"""
        self.add_message_bubble(text, is_user=False)
        self.conversation.append({"role": "assistant", "content": text})

    def add_message_bubble(self, text, is_user=False):
        """Add a message bubble to the chat container"""
        sender = "Bạn" if is_user else "AI"
        full_text = f"{sender}:\n{text}"
        
        msg_btn = RoundedButton(
            text=full_text,
            size_hint=(None, None),
            width=320,
            halign="right",
            valign="middle",
            text_size=(280, None)
        )
        
        if is_user:
            msg_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)  # Orange for user
        else:
            msg_btn.change_color(0.9, 0.4, 0.1, 1)  # Darker orange for assistant
            
        msg_btn.color = (0, 0, 0, 1)  # Black text
        msg_btn.bind(texture_size=lambda b, ts: setattr(b, 'height', ts[1] + 20))
        
        # Position messages
        msg_btn.pos_hint = {"x": 0}
        
        self.container.add_widget(msg_btn)
        # Scroll to bottom
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)

    def send_message(self, instance):
        if len(self.conversation) > 5:
            self.conversation.pop(0)
        """Send a message to the AI service"""
        text = self.input_text.text.strip()
        if not text:
            return
            
        # Add user message to UI
        self.add_user_message(text)
        print("User message added to UI")
        
        # Clear input field
        self.input_text.text = ""
        
        # Prepare request payload
        payload = {
            "message": text,
            "role": "user",
            "converstation": self.conversation
        }
        Thread(target=self.make_ai_req, args=(payload,),daemon=True).start()
        
        # Send request to AI service
        pass
    def make_ai_req(self, payload, base_url = "http://localhost:8013/chat"):
        response = requests.post(base_url, json=payload)
        if response.status_code == 200:
            self.add_assistant_message(response.text)
        else:
            self.add_assistant_message(f"Xin lỗi, tôi gặp lỗi khi xử lý yêu cầu của bạn. (Lỗi: {response.status_code})")
    def remove_message(self, message_text):
        pass
