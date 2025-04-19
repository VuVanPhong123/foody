from frontend.welcomeScreen import WelcomeScreen
from frontend.logScreen import LogScreen
from frontend.mainscreen import MainScreen
from frontend.settingsScreenOwner import SettingsScreenOwner
from frontend.chatScreenOwn import ChatScreenCus
from frontend.changePass import ChangePasswordScreen
from kivy.app import App
from kivy.uix.screenmanager import Screen,ScreenManager,FallOutTransition
from kivymd.app import MDApp
class Foody(MDApp):
    def build(self):
        sm=ScreenManager()
        sm = ScreenManager(transition=FallOutTransition()) 
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(LogScreen(name='log'))
        sm.add_widget(MainScreen(name='mainscreen'))
        sm.add_widget(SettingsScreenOwner(name="settings_owner"))
        sm.add_widget(ChatScreenCus(name="chat"))
        sm.add_widget(ChangePasswordScreen(name="pass"))
        return sm

