from frontend.welcomeScreencus import WelcomeScreen
from frontend.logScreencus import LogScreen
from frontend.mainScreenCus import MainScreenCus
from frontend.settingsScreen import SettingsScreen
from kivy.app import App
from kivy.uix.screenmanager import Screen,ScreenManager,FallOutTransition
from kivymd.app import MDApp
class Foody(MDApp):
    def build(self):
        sm=ScreenManager()
        sm = ScreenManager(transition=FallOutTransition()) 
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(LogScreen(name='log'))    
        sm.add_widget(MainScreenCus(name='mainscreen'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

