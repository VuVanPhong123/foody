from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.widget import Widget  # Import Widget for empty spaces
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config
from kivy.graphics import Color, Rectangle
# Set window size (width, height)
Config.set('graphics', 'width', '350')
Config.set('graphics', 'height', '600')

# Disable resizing
Config.set('graphics', 'resizable', False)
from kivymd.uix.button import MDFlatButton, MDFloatingActionButton
from kivymd.app import MDApp

class WelcomeScreen(FloatLayout):
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
            pos_hint={'center_x': 0.5, 'top': 0.9}  
        ))

        # Centered Button
        button = MDFloatingActionButton(
            icon="arrow-right",
            md_bg_color=(233/255,150/255,14/255, 1),  # Red button
            pos_hint={'center_x': 0.78, 'center_y': 0.1}  # Centered
        )
        self.add_widget(button)
        button.bind(on_press=self.pressed)
        self.add_widget(Image(
            source="logo.png",  # Change to your image file
            size_hint=(None, None),
            size=(600, 600),  # Adjust the size of the image
            pos_hint={'center_x': 0.5, 'center_y': 0.5}  # Adjust position
        ))
    def pressed(self, instance):
        print("phong")

    def update_rect(self, *args):
        """ Update the background size when the window is resized """
        self.rect.size = self.size
        self.rect.pos = self.pos

class MyApp(MDApp):
    def build(self):
        return WelcomeScreen()

if __name__ == "__main__":
    MyApp().run()
