from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FallOutTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class TabBar(BoxLayout):
    """ Fixed Tab Bar on Top """
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = 0.1  # 10% of screen height
        self.screen_manager = screen_manager

        # Create Tab Buttons
        self.home_button = Button(text="🏠 Home", on_press=lambda x: self.switch_tab("home"))
        self.settings_button = Button(text="⚙️ Settings", on_press=lambda x: self.switch_tab("settings"))

        self.add_widget(self.home_button)
        self.add_widget(self.settings_button)

    def switch_tab(self, tab_name):
        """ Switch the active screen with a fade effect """
        self.screen_manager.current = tab_name

class HomeScreen(Screen):
    """ Home Screen Content """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Welcome to Home Screen!", font_size=24))
        self.add_widget(layout)

class SettingsScreen(Screen):
    """ Settings Screen Content """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Settings Page", font_size=24))
        self.add_widget(layout)

class MainApp(App):
    def build(self):
        # Main Layout
        root_layout = BoxLayout(orientation="vertical")

        # Screen Manager with FadeTransition
        sm = ScreenManager(transition=FallOutTransition(duration=0.5))  # Fade effect
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(SettingsScreen(name="settings"))

        # Tab Bar (Stays on top)
        tab_bar = TabBar(screen_manager=sm)

        # Add tab bar and screen manager to the main layout
        root_layout.add_widget(tab_bar)
        root_layout.add_widget(sm)

        return root_layout

if __name__ == "__main__":
    MainApp().run()
