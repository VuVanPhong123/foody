import welcomeScreen
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.config import Config
# Set window size (width, height)

from kivymd.uix.button import MDFlatButton, MDFloatingActionButton
from kivymd.app import MDApp

class foody(MDApp):
    def build(self):
        return welcomeScreen.WelcomeScreen()