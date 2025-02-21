import foody
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.config import Config
# Set window size (width, height)
Config.set('graphics', 'width', '350')
Config.set('graphics', 'height', '600')

# Disable resizing
Config.set('graphics', 'resizable', False)
from kivymd.uix.button import MDFlatButton, MDFloatingActionButton
from kivymd.app import MDApp

if __name__ == '__main__':
    foody.foody().run()