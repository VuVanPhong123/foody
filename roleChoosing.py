from roundButton import RoundedButton
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.widget import Widget  # Import Widget for empty spaces
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen,ScreenManager
from kivy.config import Config
from kivy.graphics import Color, RoundedRectangle, Rectangle

# Set window size (width, height)
Config.set('graphics', 'width', '350')
Config.set('graphics', 'height', '600')

# Disable resizing
Config.set('graphics', 'resizable', False)

from kivymd.uix.button import MDFlatButton, MDFloatingActionButton
from kivymd.app import MDApp
from kivymd.uix.card import MDCard

class RoleChoosing(Screen):
    def __init__(self, **kwargs):
        super(RoleChoosing, self).__init__(**kwargs)
        
        # Background Color
        with self.canvas.before:
            Color(245/255, 177/255, 67/255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        # Title Label
        self.add_widget(Label(
            text="Bạn là...",
            font_size=24,
            size_hint=(None, None), 
            size=(150, 50),
            pos_hint={'center_x': 0.2, 'top': 0.9}  
        ))

        # Arrow Button
        button = MDFloatingActionButton(
            icon="arrow-right",
            md_bg_color=(233/255, 150/255, 14/255, 1),  
            pos_hint={'center_x': 0.78, 'center_y': 0.1}  
        )
        self.add_widget(button)

        # Initialize state variables
        self.StateOp1 = 0
        self.StateOp2 = 0

        # Owner Button
        self.btnOption1 = RoundedButton(
            text="Chủ nhà hàng",
            size_hint=(None, None),
            size=(200, 80),
            font_size=20,
            pos=(80, 300)
        )
        self.btnOption1.change_color(233/255, 150/255, 14/255, 1)
        self.add_widget(self.btnOption1)

        # Customer Button
        self.btnOption2 = RoundedButton(
            text="Khách hàng",
            size_hint=(None, None),
            size=(200, 80),
            font_size=20,
            pos=(80, 200)  
        )
        self.btnOption2.change_color(233/255, 150/255, 14/255, 1) 
        self.add_widget(self.btnOption2)

        # Bind Buttons
        self.btnOption1.bind(on_press=self.pressed1)
        self.btnOption2.bind(on_press=self.pressed2)

    def pressed1(self, instance):
        if self.StateOp1 == 0:
            if self.StateOp2 == 0:
                self.btnOption1.big(1)
                self.btnOption2.shrink(1)
                self.StateOp1 = 1
                self.StateOp2 = 0
            elif self.StateOp2 == 1:
                self.btnOption1.big(2)
                self.btnOption2.shrink(2)
                self.StateOp1 = 1
                self.StateOp2 = 0

    def pressed2(self, instance):
        if self.StateOp2 == 0:
            if self.StateOp1 == 0:
                self.btnOption2.big(1)
                self.btnOption1.shrink(1)
                self.StateOp2 = 1
                self.StateOp1 = 0
            elif self.StateOp1 == 1:
                self.btnOption2.big(2)
                self.btnOption1.shrink(2)
                self.StateOp2 = 1
                self.StateOp1 = 0

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos


