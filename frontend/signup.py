from frontend.roundButton import RoundedButton
import pandas as pd
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.widget import Widget  
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen,ScreenManager
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivymd.uix.button import MDFlatButton, MDFloatingActionButton,MDIconButton
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
class SignUp(Screen):
    def __init__(self, **kwargs):
        super(SignUp, self).__init__(**kwargs)
        
        # Background Color
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
        self.add_widget(Label(
            text="Xác nhận: ",
            font_size=15,
            size_hint=(None, None), 
            size=(150, 50),
            pos_hint={'center_x': 0.2, 'top': 0.5}  
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
        self.float = FloatLayout()
        self.ConfirmPassword = MDTextField(hint_text='xác nhận mật khẩu', multiline=False,
                              pos_hint={'x': 0.32, 'y': 0.41},size_hint_x=0.48,password=True)
        self.float.add_widget(self.ConfirmPassword)
        self.add_widget(self.float)
        self.eye_button = MDIconButton(
            icon="eye-off", 
            md_bg_color=(233/255, 150/255, 14/255, 1),
            pos_hint={'center_x': 0.87, 'center_y': 0.56},
            icon_size="15sp",  
            on_release=self.toggle_password
        )
        self.add_widget(self.eye_button)

        self.eye_button2 = MDIconButton(
            icon="eye-off", 
            md_bg_color=(233/255, 150/255, 14/255, 1),
            pos_hint={'center_x': 0.87, 'center_y': 0.46},
            icon_size="15sp",  
            on_release=self.toggle_confirm_password
        )
        self.add_widget(self.eye_button2)
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

        self.btnOption1 = RoundedButton(
            text="Đăng ký",
            size_hint=(0.45, 0.07),  
            font_size=25,
            pos_hint={"center_x": 0.5, "center_y": 0.3} 
        )
        self.btnOption1.change_color(233/255, 150/255, 14/255, 1)
        self.add_widget(self.btnOption1)
        self.btnOption1.bind(on_press=self.pressed1)
        Notification=''
        self.notice=Label(
            text=Notification,
            font_size=10,
            size_hint=(None, None), 
            size=(150, 50),
            color=(1, 0, 0, 1),
            pos_hint={'center_x': 0.5, 'top': 0.28}  
        )
        self.add_widget(self.notice)

    def go_back(self,instance):
        self.manager.current = 'log' 
    def toggle_password(self, instance):
        if self.Password.password:
            self.Password.password = False  # Show text
            self.eye_button.icon = "eye"  # Change icon to open eye
        else:
            self.Password.password = True  # Hide text
            self.eye_button.icon = "eye-off"  # Change icon to closed eye
    def toggle_confirm_password(self, instance):
        if self.ConfirmPassword.password:
            self.ConfirmPassword.password = False  # Show text
            self.eye_button2.icon = "eye"  # Change icon to open eye
        else:
            self.ConfirmPassword.password = True  # Hide text
            self.eye_button2.icon = "eye-off"  # Change icon to closed eye
    def pressed1(self, instance):

        df = pd.read_csv("data/cusAccList.csv")
        row = df[df["acc"] == self.acc.text]
        if self.Password.text =='':
            self.Notification='Vui lòng điền mật khẩu'
        elif self.ConfirmPassword.text =='':
            self.Notification='Vui lòng xác nhận mật khẩu'
        elif not row.empty:
            self.Notification='Tên tài khoản đã được sử dụng'
        elif self.Password.text != self.ConfirmPassword.text:
            self.Notification='Mật khẩu không trùng khớp!'
        else:
            self.Notification='Đăng ký thành công'
            new_row = {"acc": self.acc.text, "pass": self.Password.text}
            df = pd.read_csv("data/cusAccList.csv")
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv("data/cusAccList.csv", index=False)
        self.notice.text=self.Notification
    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
class app(MDApp):
    def build(self):
        return SignUp()
if __name__ == '__main__':
    app().run()


