from frontend.welcomeScreencus import WelcomeScreen
from frontend.logScreencus import LogScreen
from frontend.logDelayTest import LogDelayTest
from frontend.logEndpointChangeTest import LogEndpointChangeTest
from frontend.logGarbageCharTest import LogGarbageCharTest
from frontend.mainScreenCus import MainScreenCus
from frontend.settingsScreen import SettingsScreen
from frontend.reviewScreen import ReviewScreen
from frontend.chatScreenCus import ChatScreenCus
from frontend.changePasswordScreenCus import ChangePasswordScreen
from frontend.signupScreencus import SignUpScreen
from kivy.uix.screenmanager import ScreenManager, FallOutTransition
from kivymd.app import MDApp

class Foody(MDApp):
    def build(self):
        sm = ScreenManager(transition=FallOutTransition())
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(LogScreen(name='log'))
        #sm.add_widget(LogDelayTest(name='log'))
        #sm.add_widget(LogEndpointChangeTest(name='log'))
        #sm.add_widget(LogGarbageCharTest(name='log'))
        sm.add_widget(SignUpScreen(name='signup'))
        sm.add_widget(MainScreenCus(name='mainscreen'))
        sm.add_widget(SettingsScreen(name='settings')) 
        sm.add_widget(ReviewScreen(name="review"))
        sm.add_widget(ChatScreenCus(name="chat"))
        sm.add_widget(ChangePasswordScreen(name="changepass"))
        return sm
