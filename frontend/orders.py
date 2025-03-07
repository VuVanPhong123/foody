from frontend.roundButton import RoundedButton
from frontend.makingorders import Makingorders
from frontend.onlineorders import Onlineorders
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout

from kivy.uix.screenmanager import Screen, ScreenManager,FallOutTransition
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from kivymd.app import MDApp

class Orders(Screen):
    def __init__(self, **kwargs):
        super(Orders, self).__init__(**kwargs)
        with self.canvas.before:
            Color(245/255, 177/255, 67/255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        root = BoxLayout(orientation='vertical')
        tab_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='30dp'
        )
        self.btnOption1 = RoundedButton(
            text="Đơn hàng",
            size_hint=(0.45, 0.7),  
            font_size=20,
        )
        self.btnOption1.change_color(233/255, 150/255, 14/255, 1)
        self.btnOption1.color = (0, 0, 0, 1)
        tab_bar.add_widget(self.btnOption1)
        self.btnOption1.bind(on_press=self.pressed1)  
        
        self.btnOption2 = RoundedButton(
            text="Đơn online",
            size_hint=(0.45, 0.7),  
            font_size=20,
        )
        self.btnOption2.change_color(233/255, 150/255, 14/255, 1)
        self.btnOption2.color = (0, 0, 0, 1)
        tab_bar.add_widget(self.btnOption2)
        self.btnOption2.bind(on_press=self.pressed2)   
        root.add_widget(tab_bar)  
        
        self.screen_manager = ScreenManager()
        self.screen_manager=ScreenManager(transition=FallOutTransition()) 
        self.screen_manager.add_widget(Makingorders(name="tao_order"))
        self.screen_manager.add_widget(Onlineorders(name="online_order"))
        
        root.add_widget(self.screen_manager)
        self.add_widget(root)
        
       
    def pressed1(self, instance):
        self.btnOption2.change_color(233 / 255, 150 / 255, 14 / 255, 1)
        self.btnOption2.color = (0, 0, 0, 1)
        self.btnOption1.change_color(200 / 255, 100 / 255, 14 / 255, 1)
        self.btnOption1.color = (0, 0, 0, 1)
        self.screen_manager.current="tao_order"
    def pressed2(self, instance):
        self.btnOption1.change_color(233 / 255, 150 / 255, 14 / 255, 1)
        self.btnOption1.color = (0, 0, 0, 1)
        self.btnOption2.change_color(200 / 255, 100 / 255, 14 / 255, 1)
        self.btnOption2.color = (0, 0, 0, 1)
        self.screen_manager.current="online_order"
    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

class app(MDApp):
    def build(self):
        return Orders()

if __name__ == '__main__':
    app().run()
