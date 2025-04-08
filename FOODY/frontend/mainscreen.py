from datetime import datetime
from frontend.roundButton import RoundedButton
from frontend.orders import Orders
from frontend.ingredient import Ingredients
from frontend.revenue import Revenue
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager, FallOutTransition
from kivy.graphics import Color, Rectangle
from kivymd.uix.button import MDIconButton
from kivymd.app import MDApp

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        with self.canvas.before:
            Color(245/255, 177/255, 67/255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)
        self.active_tab = None

        # Main layout
        root = BoxLayout(orientation='vertical')

        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='50dp',
            padding=('10dp', '5dp'),
            spacing='10dp'
        )

        self.greeting_label = Label(
            text='FOODY',
            
            color=(0, 0, 0, 1),
            halign="left",
            valign="middle",
            size_hint=(0.4,1 ),
            
        )
        self.greeting_label.bind(size=self.greeting_label.setter('text_size'))
        self.bind(size=self.update_font_size)

        self.date_label = Label(
            text=self.get_vietnamese_date_string(),  
            font_size=(self.width+self.height)/2 * 0.035,
            color=(0, 0, 0, 1),
            halign="right",
            valign="middle",
            size_hint=(1, 1)
        )
        self.date_label.bind(size=self.date_label.setter('text_size'))

        settings_button = MDIconButton(
            icon="cog",
            md_bg_color=(233/255, 150/255, 14/255, 1),
            icon_size="20sp",
        )

        top_bar.add_widget(self.greeting_label)
        top_bar.add_widget(self.date_label)
        top_bar.add_widget(settings_button)

        tab_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='40dp'
        )

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
                font_size=(self.width+self.height)/2 / 20,
            )
            btn.change_color(233/255, 150/255, 14/255, 1)
            btn.color = (0, 0, 0, 1)

            btn.bind(on_press=lambda b, sn=screen_name: self.select_tab(b, sn))
            self.buttons.append(btn)
            tab_bar.add_widget(btn)

        self.bind(size=self.update_button_font_size)

        self.screen_manager = ScreenManager(transition=FallOutTransition())
        self.screen_manager.add_widget(Orders(name="don_hang", top_manager=self.screen_manager))
        self.screen_manager.add_widget(Revenue(name="doanh_thu"))
        self.screen_manager.add_widget(Ingredients(name="nguyen_lieu"))
        self.screen_manager.add_widget(Orders(name="phan_hoi"))

        root.add_widget(top_bar)
        root.add_widget(tab_bar)
        root.add_widget(self.screen_manager)
        self.add_widget(root)

        
        if self.buttons:
            self.select_tab(self.buttons[0], "don_hang")

    def get_vietnamese_date_string(self):
        
        days_vn = ["Thứ Hai","Thứ Ba","Thứ Tư","Thứ Năm","Thứ Sáu","Thứ Bảy","Chủ Nhật"]
        now = datetime.now()
        weekday_idx = now.weekday()
        weekday_text = days_vn[weekday_idx]
        return f"{weekday_text}, ngày {now.day} tháng {now.month} năm {now.year}"

    def select_tab(self, new_button, screen_name):
        if self.active_tab and self.active_tab != new_button:
            self.active_tab.change_color(233/255, 150/255, 14/255, 1)
            self.active_tab.color = (0, 0, 0, 1)
        new_button.change_color(200/255, 100/255, 14/255, 1)
        new_button.color = (0, 0, 0, 1)
        self.active_tab = new_button
        self.screen_manager.current = screen_name

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def update_font_size(self, *args):
        self.greeting_label.font_size = (self.width+self.height)/2 / 25
        self.date_label.font_size = (self.width+self.height)/2 / 35

    def update_button_font_size(self, *args):
        for btn in self.buttons:
            btn.font_size = (self.width+self.height)/2 / 36


class MyApp(MDApp):
    def build(self):
        return MainScreen()

if __name__ == '__main__':
    MyApp().run()
