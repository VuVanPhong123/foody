from frontend.roundButton import RoundedButton
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.widget import Widget  
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen,ScreenManager
from kivy.graphics import Color, RoundedRectangle, Rectangle

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

    
        # Initialize state variables
        self.StateOp1 = 0
        self.StateOp2 = 0

        # Owner Button
        self.btnOption1 = RoundedButton(
            text="Chủ nhà hàng",
            size_hint=(0.5, 0.1),  # Adjust width and height relative to the screen
            font_size=20,
            pos_hint={"center_x": 0.5, "center_y": 0.6}  # Position relative to the screen
        )

        self.btnOption1.change_color(233/255, 150/255, 14/255, 1)
        self.add_widget(self.btnOption1)

        # Customer Button
        self.btnOption2 = RoundedButton(
            text="Khách hàng",
            size_hint=(0.5, 0.1),  # Adjust width and height relative to the screen
            font_size=20,
            pos_hint={"center_x": 0.5, "center_y": 0.4} 
        )
        self.btnOption2.change_color(233/255, 150/255, 14/255, 1) 
        self.add_widget(self.btnOption2)

        # Bind Buttons
        self.btnOption1.bind(on_press=self.pressed1)
        self.btnOption2.bind(on_press=self.pressed2)

    def generate_button(self):
        self.button = MDFloatingActionButton(
            icon="arrow-right",
            md_bg_color=(233/255, 150/255, 14/255, 1),  
            pos_hint={'center_x': 0.78, 'center_y': 0.1}  
        )
        self.add_widget(self.button)
        self.button.bind(on_press=self.go_front)
    def go_front(self,instance):
        self.manager.current='log'
    def pressed1(self, instance):
        self.btnOption1.change_color(210/255, 105/255, 30/255, 1)
        self.btnOption2.restore_color()
        self.accType = 1
        print(self.accType)
        self.generate_button()
    def pressed2(self, instance):
        self.btnOption2.change_color(210/255, 105/255, 30/255, 1)
        self.btnOption1.restore_color()
        self.accType = 2
        print(self.accType)
        self.generate_button()
    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
class app(MDApp):
    def build(self):
        return RoleChoosing()
if __name__ == '__main__':
    app().run()




