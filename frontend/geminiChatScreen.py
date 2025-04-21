import requests
from frontend.aiChatScreen import AIChatScreen
from frontend.roundButton import RoundedButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
import os
from kivy.uix.boxlayout import BoxLayout



class GeminiChatScreen(AIChatScreen):
    def __init__(self, **kwargs):
        super(GeminiChatScreen, self).__init__(**kwargs)
        self.ai_avatar = os.path.join(os.path.dirname(__file__), "assets/gemini.png")


    
    def add_message_bubble(self, text, is_user=False):
        sender = "Bạn" if is_user else "AI"
        full_text = f"{sender}:\n{text}"

        # Tạo bubble
        msg_btn = RoundedButton(
            text=full_text,
            size_hint=(None, None),
            width=320,
            halign="left",
            valign="middle",
            text_size=(280, None)
        )
        msg_btn.color = (0, 0, 0, 1)
        msg_btn.bind(texture_size=lambda b, ts: setattr(b, 'height', ts[1] + 20))
        msg_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1) if is_user else msg_btn.change_color(0.9, 0.4, 0.1, 1)

        # Tạo avatar tròn
        avatar = Image(source=self.ai_avatar, size_hint=(None, None), size=(40, 40))

        # Tạo layout cho một dòng chat
        line = BoxLayout(orientation="horizontal", size_hint=(1, None), height=msg_btn.height + 20)

        # Căn trái/phải tùy thuộc vào người gửi
        if is_user:
            line.add_widget(BoxLayout(size_hint_x=0.1))  # Spacer trái
            line.add_widget(msg_btn)
        else:
            line.add_widget(avatar)
            line.add_widget(msg_btn)
            line.add_widget(BoxLayout(size_hint_x=0.1))  # Spacer phải

        self.container.add_widget(line)
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)


            




    def go_back(self, instance):
        self.manager.current = "menu_screen"
