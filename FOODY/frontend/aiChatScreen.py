from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivymd.uix.button import MDFloatingActionButton
from kivy.graphics import Color, Rectangle
from frontend.roundButton import RoundedButton
from kivy.graphics import RoundedRectangle
from kivy.clock import Clock
import requests
from kivymd.uix.label import MDLabel
from kivy.metrics import dp

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
        back_btn = MDFloatingActionButton(
            icon="arrow-left",
            md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1),
            icon_color=(0, 0, 0, 1),
            size_hint=(None, None),
            size=("20dp", "20dp")
        )
        back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(back_btn)

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

    def go_back(self, instance):
        """Navigate back to previous screen"""
        self.manager.current = "mainscreen"  # Adjust based on your navigation flow

    def on_leave(self, *args):
        """Clean up resources when leaving the screen"""
        # Clean up texture cache to free memory
        self.cleanup_messages()

    def add_user_message(self, text):
        """Add a user message to the chat"""
        self.add_message_bubble(text, is_user=True)
        self.conversation.append({"role": "user", "content": text})

    def add_assistant_message(self, text):
        """Add an assistant message to the chat"""
        self.add_message_bubble(text, is_user=False)
        self.conversation.append({"role": "assistant", "content": text})

    def add_message_bubble(self, text, is_user=False):
        """Add a message bubble to the chat container with Markdown support"""
        sender = "Bạn" if is_user else "AI"
        full_text = f"**{sender}**:\n{text}"  # Make sender bold using Markdown

        # Create a container for the message
        msg_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[10, 5, 10, 5],  # Left, Top, Right, Bottom padding
            spacing=5
        )

        # Create the label with Markdown support
        msg_label = MDLabel(
            text=full_text,
            markup=True,  # Enable markup/markdown
            size_hint_y=None,
            adaptive_height=True,  # Automatically adjust height
            padding=[15, 10],  # Text padding inside the label
            halign="left",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1)  # Black text
        )

        # Bind the label height to ensure proper sizing
        msg_label.bind(
            width=lambda *x: setattr(msg_label, 'text_size', (msg_label.width - dp(20), None)),
            texture_size=lambda *x: setattr(msg_label, 'height', msg_label.texture_size[1])
        )

        # Set background color based on sender
        with msg_container.canvas.before:
            Color(*(
                (233/255, 150/255, 14/255, 1) if is_user  # Orange for user
                else (0.9, 0.4, 0.1, 1)  # Darker orange for assistant
            ))
            RoundedRectangle(
                pos=msg_container.pos,
                size=msg_container.size,
                radius=[15,]
            )

        # Update the background when the container size/pos changes
        msg_container.bind(
            pos=lambda *x: setattr(msg_container.canvas.before.children[-1], 'pos', msg_container.pos),
            size=lambda *x: setattr(msg_container.canvas.before.children[-1], 'size', msg_container.size)
        )

        # Add label to container
        msg_container.add_widget(msg_label)

        # Set container width and position
        msg_container.size_hint_x = 0.8
        msg_container.pos_hint = {"x": 0}

        # Add to main container
        self.container.add_widget(msg_container)

        # Force immediate UI update in 3 steps:
        # 1. Refresh container layout
        self.container.do_layout()

        # 2. Force canvas update
        msg_container.canvas.ask_update()

        # 3. Schedule scroll to bottom
        Clock.schedule_once(self.scroll_to_bottom, 0)

    def remove_message(self, message_text):
        """Remove a message from the conversation history"""
        # Find the index of the message in the conversation history
        for i, msg in enumerate(self.conversation):
            if msg.get("content") == message_text:
                # Remove from conversation history
                self.conversation.pop(i)
                # Remove the corresponding widget from the UI
                if i < len(self.container.children):
                    self.container.remove_widget(self.container.children[i])
                    # Force layout update after removal
                    self.container.do_layout()
                    # Request canvas update
                    self.container.canvas.ask_update()
                break

    def scroll_to_bottom(self, dt):
        """Scroll to the newest message"""
        if len(self.container.children) > 0:
            self.scroll.scroll_to(self.container.children[0])
            # Alternative method if the above doesn't work well
            self.scroll.scroll_y = 0

    def send_message(self, instance):
        """Send a message to the AI service with better UI responsiveness"""
        text = self.input_text.text.strip()
        if not text:
            return

        # Add user message with immediate UI update
        self.add_user_message(text)

        # Clear input field
        self.input_text.text = ""

        # Force focus back to input (better UX)
        self.input_text.focus = True

        # Prepare request payload
        payload = {
            "message": text,
            "role": "user"
        }

        # Create a placeholder for the AI response (optional loading indicator)
        loading_message = "Đang xử lý..."
        self.add_assistant_message(loading_message)

        # Send request to AI service
        try:
            resp = requests.post("http://localhost:8011/chat", json=payload)
            if resp.status_code == 200:
                # Remove loading message and add actual response
                self.remove_message(loading_message)
                self.add_assistant_message(resp.text)
            else:
                # Remove loading message and show error
                self.remove_message(loading_message)
                self.add_assistant_message(f"Xin lỗi, tôi gặp lỗi khi xử lý yêu cầu của bạn. (Lỗi: {resp.status_code})")
        except Exception as e:
            # Remove loading message and show connection error
            self.remove_message(loading_message)
            self.add_assistant_message(f"Xin lỗi, tôi không thể kết nối đến máy chủ. (Lỗi: {str(e)})")

    def cleanup_messages(self):
        """Clear texture cache if you have many messages"""
        from kivy.core.image import Image
        Image.textures.clear()