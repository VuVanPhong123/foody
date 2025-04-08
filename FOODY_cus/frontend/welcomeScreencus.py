from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.widget import Widget  # Import Widget for empty spaces
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen,ScreenManager
from kivy.graphics import Color, Rectangle

from kivymd.uix.button import MDFlatButton, MDFloatingActionButton
from kivymd.app import MDApp

class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super(WelcomeScreen, self).__init__(**kwargs)
        with self.canvas.before:
            Color(245/255,177/255,67/255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)
        self.add_widget(Label(
            text="Welcome to foody!",
            font_size=24,
            size_hint=(None, None), 
            size=(150, 50),
            pos_hint={'center_x': 0.5, 'top': 0.9},
            color=(0, 0, 0, 1)
        ))

        # Centered Button
        button = MDFloatingActionButton(
            icon="arrow-right",
            md_bg_color=(233/255,150/255,14/255, 1),  
            pos_hint={'center_x': 0.78, 'center_y': 0.1}
            
        )
        self.add_widget(button)
        button.bind(on_press=self.go_to_role_screen)
        self.add_widget(Image(
            source="images/logo.png",  
            size_hint=(None, None),
            size=(600, 600),  
            pos_hint={'center_x': 0.5, 'center_y': 0.5}  
        ))

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
    def go_to_role_screen(self, instance):
            self.manager.current = 'log' 
class app(MDApp):
    def build(self):
        return WelcomeScreen()
if __name__ == '__main__':
    app().run()

