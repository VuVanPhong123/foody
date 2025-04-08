from frontend.roundButton import RoundedButton 
import pandas as pd
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.widget import Widget 
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen, ScreenManager

from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivymd.uix.button import MDFlatButton, MDFloatingActionButton, MDIconButton
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField

class LogScreen(Screen):
    def __init__(self, **kwargs):
        super(LogScreen, self).__init__(**kwargs)
    
        with self.canvas.before:
            Color(245/255, 177/255, 67/255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.add_widget(Image(
            source="images/logo.png",  
            size_hint=(None, None),
            size=(400, 400),  
            pos_hint={'center_x': 0.5, 'center_y': 0.82}  
        ))
        self.add_widget(Label(
            text="Mật khẩu: ",
            font_size=20,
            size_hint=(None, None), 
            size=(150, 50),
            pos_hint={'center_x': 0.2, 'top': 0.6},
            color=(0, 0, 0, 1)
        ))
        self.float = FloatLayout()
        self.Password = MDTextField(
            hint_text='mật khẩu', 
            multiline=False,
            pos_hint={'x': 0.32, 'y': 0.51},
            size_hint_x=0.48,
            password=True
        )
        self.float.add_widget(self.Password)
        self.add_widget(self.float)
        
        self.eye_button = MDIconButton(
            icon="eye-off", 
            md_bg_color=(233/255, 150/255, 14/255, 1),
            pos_hint={'center_x': 0.87, 'center_y': 0.56},
            icon_size="15sp",  
            on_release=self.toggle_password
        )
        self.add_widget(self.eye_button)
        
        self.button = MDFloatingActionButton(
            icon="arrow-left",
            md_bg_color=(233/255, 150/255, 14/255, 1),  
            pos_hint={'center_x': 0.18, 'center_y': 0.1}  
        )
        self.add_widget(self.button)
        self.button.bind(on_press=self.go_back)

        self.btnOption1 = RoundedButton(
            text="Đăng Nhập",
            size_hint=(0.45, 0.07),  
            font_size=25,
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            color=(0, 0, 0, 1)
        )
        self.btnOption1.change_color(233/255, 150/255, 14/255, 1)
        self.btnOption1.color = (0, 0, 0, 1)
        self.add_widget(self.btnOption1)
        self.btnOption1.bind(on_press=self.pressed1)
        
        self.times = 0

    def go_back(self, instance):
        self.manager.current = 'welcome' 

    def toggle_password(self, instance):
        if self.Password.password:
            self.Password.password = False  # Show text
            self.eye_button.icon = "eye"       # Change icon to open eye
        else:
            self.Password.password = True      # Hide text
            self.eye_button.icon = "eye-off"     # Change icon to closed eye

    def pressed1(self, instance):
        if self.Password.text == "1":
            print('đăng nhập thành công')
            self.manager.current = 'mainscreen'
        else:
            if self.times == 0:
                self.add_widget(Label(
                    text="Mật khẩu sai! ",
                    font_size=15,
                    size_hint=(None, None), 
                    size=(150, 50),
                    color=(1, 0, 0, 1),
                    pos_hint={'center_x': 0.5, 'top': 0.35}
                ))
            self.times += 1

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

