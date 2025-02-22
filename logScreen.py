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

from kivymd.uix.button import MDFlatButton, MDFloatingActionButton,MDIconButton
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
class LogScreen(Screen):
    def __init__(self, **kwargs):
        super(LogScreen, self).__init__(**kwargs)
        
        # Background Color
        with self.canvas.before:
            Color(245/255, 177/255, 67/255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.add_widget(Image(
            source="logo.png",  
            size_hint=(None, None),
            size=(400, 400),  
            pos_hint={'center_x': 0.5, 'center_y': 0.82}  
        ))
        # Title Label
        self.add_widget(Label(
            text="Tài khoản: ",
            font_size=15,
            size_hint=(None, None), 
            size=(150, 50),
            pos_hint={'center_x': 0.2, 'top': 0.7}  
        ))
        self.add_widget(Label(
            text="Mật khẩu: ",
            font_size=15,
            size_hint=(None, None), 
            size=(150, 50),
            pos_hint={'center_x': 0.2, 'top': 0.6}  
        ))
        self.float = FloatLayout()
        self.acc = MDTextField(hint_text='tài khoản', multiline=False,
                              pos_hint={'x': 0.32, 'y': 0.61},size_hint_x=0.48,)
        self.float.add_widget(self.acc)
        self.add_widget(self.float)
        self.float = FloatLayout()
        self.Password = MDTextField(hint_text='mật khẩu', multiline=False,
                              pos_hint={'x': 0.32, 'y': 0.51},size_hint_x=0.48,password=True)
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

        # Arrow Button
        self.button = MDFloatingActionButton(
            icon="arrow-left",
            md_bg_color=(233/255, 150/255, 14/255, 1),  
            pos_hint={'center_x': 0.18, 'center_y': 0.1}  
        )
        self.add_widget(self.button)
        self.button.bind(on_press=self.go_back)

        # Initialize state variables
        self.StateOp1 = 0
        self.StateOp2 = 0

        # Owner Button
        self.btnOption1 = RoundedButton(
            text="Đăng Nhập",
            size_hint=(None, None),
            size=(125, 50),
            font_size=15,
            pos=(117.5, 245)
        )
        self.btnOption1.change_color(233/255, 150/255, 14/255, 1)
        self.add_widget(self.btnOption1)

        # Customer Button
        self.btnOption2 = RoundedButton(
            text="Bạn chưa có tài khoản?",
            size_hint=(None, None),
            size=(170, 34),
            font_size=15,
            pos=(95, 203)  
        )
        self.btnOption2.change_color(233/255, 150/255, 14/255, 1) 
        self.add_widget(self.btnOption2)

        # Bind Buttons
        self.btnOption1.bind(on_press=self.pressed1)
        self.btnOption2.bind(on_press=self.pressed2)

    def go_back(self,instance):
        self.manager.current = 'role' 
    def toggle_password(self, instance):
        if self.Password.password:
            self.Password.password = False  # Show text
            self.eye_button.icon = "eye"  # Change icon to open eye
        else:
            self.Password.password = True  # Hide text
            self.eye_button.icon = "eye-off"  # Change icon to closed eye

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
class app(MDApp):
    def build(self):
        return LogScreen()
if __name__ == '__main__':
    app().run()


