from frontend.welcomeScreen import WelcomeScreen
from frontend.roleChoosing import RoleChoosing
from frontend.logScreen import LogScreen

from kivy.app import App
from kivy.uix.screenmanager import Screen,ScreenManager,FallOutTransition
from kivymd.app import MDApp

class Foody(MDApp):
    def build(self):
        sm=ScreenManager()
        sm = ScreenManager(transition=FallOutTransition()) 
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(RoleChoosing(name='role'))
        sm.add_widget(LogScreen(name='log'))
        return sm

