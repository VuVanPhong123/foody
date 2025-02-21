from welcomeScreen import WelcomeScreen
from roleChoosing import RoleChoosing
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen,ScreenManager
from kivy.config import Config
# Set window size (width, height)

from kivymd.uix.button import MDFlatButton, MDFloatingActionButton
from kivymd.app import MDApp

class Foody(MDApp):
    def build(self):
        sm=ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(RoleChoosing(name='role'))
        return sm
