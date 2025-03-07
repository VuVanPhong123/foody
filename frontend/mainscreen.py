from frontend.roundButton import RoundedButton
from frontend.orders import Orders

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager,FallOutTransition
from kivy.graphics import Color, Rectangle
from kivymd.uix.button import MDIconButton
from kivymd.app import MDApp

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        # Background Color
        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)  # Background color
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        root = BoxLayout(orientation='vertical')

        # ========== Top Bar ==========
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='50dp',
            padding=('10dp', '5dp'),
            spacing='10dp'
        )

        # Left-aligned greeting label
        self.greeting_label = Label(
            text='FOODY', 
            font_size=self.width * 0.05,  
            color=(0, 0, 0, 1),  # Set text color to black
            halign="left",
            valign="middle",
            size_hint_x=0.9  # Takes most of the width
        )
        self.greeting_label.bind(size=self.greeting_label.setter('text_size'))
        self.bind(size=self.update_font_size)

        # Settings Button
        settings_button = MDIconButton(
            icon="cog",
            md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1),
            icon_size="20sp",
        )

        top_bar.add_widget(self.greeting_label)
        top_bar.add_widget(settings_button)

        # ========== Tab Bar ==========
        tab_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='40dp'
        )

        # Tab buttons
        self.tabs = [
            ("Đơn hàng", "don_hang"),
            ("Doanh thu", "doanh_thu"),
            ("Nguyên liệu", "nguyen_lieu"),
            ("Phản hồi", "phan_hoi"),
        ]

        self.buttons = []
        for text, screen_name in self.tabs:
            btn = RoundedButton(
                text=text,
                size_hint=(0.25, 1),
                font_size=self.width / 20,  
            )
            btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            btn.color = (0, 0, 0, 1)
            btn.bind(on_press=lambda x, sn=screen_name: self.switch_tab(sn))
            self.buttons.append(btn)
            tab_bar.add_widget(btn)

        # Bind tab buttons to resize with window
        self.bind(size=self.update_button_font_size)
        # Screen Manager
        self.screen_manager = ScreenManager()
        self.screen_manager=ScreenManager(transition=FallOutTransition()) 
        self.screen_manager.add_widget(Orders(name="don_hang"))
        self.screen_manager.add_widget(Orders(name="doanh_thu"))
        self.screen_manager.add_widget(Orders(name="nguyen_lieu"))
        self.screen_manager.add_widget(Orders(name="phan_hoi"))

        # Add widgets to layout
        root.add_widget(top_bar)
        root.add_widget(tab_bar)
        root.add_widget(self.screen_manager)
        self.add_widget(root)

    def switch_tab(self, screen_name):
        """Switches the current screen in the ScreenManager."""
        self.screen_manager.current = screen_name

    def update_rect(self, *args):
        """Update background size on window resize."""
        self.rect.size = self.size
        self.rect.pos = self.pos

    def update_font_size(self, *args):
        """Update greeting label font size on window resize."""
        self.greeting_label.font_size = self.width /18

    def update_button_font_size(self, *args):
        """Update tab button font sizes on window resize."""
        for btn in self.buttons:
            btn.font_size = self.width / 25


# App Class
class MyApp(MDApp):
    def build(self):
        return MainScreen()


if __name__ == '__main__':
    MyApp().run()
