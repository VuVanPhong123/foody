from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivymd.app import MDApp

class Makeorders(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_order = []  # Danh sách món đang chọn
        self.orders_list = []  # Lưu danh sách đơn hàng

        # Layout chính
        self.layout = FloatLayout()

        # Nút tạo đơn hàng (+)
        self.create_order_btn = Button(
            text="+",
            size_hint=(0.1, 0.08),
            pos_hint={"x": 0.05, "y": 0.05},
        )
        self.create_order_btn.bind(on_press=self.show_menu)

        # Layout hiển thị danh sách đơn hàng (BÊN TRÁI)
        self.orders_layout = BoxLayout(orientation="vertical", size_hint_y=None)
        self.orders_layout.bind(minimum_height=self.orders_layout.setter("height"))

        self.orders_scroll = ScrollView(size_hint=(0.4, 0.6), pos_hint={"x": 0.05, "y": 0.3})
        self.orders_scroll.add_widget(self.orders_layout)

        # Thêm vào layout chính
        self.layout.add_widget(self.create_order_btn)
        self.layout.add_widget(self.orders_scroll)
        self.add_widget(self.layout)

    def show_menu(self, instance):
        """ Hiển thị menu khi bấm nút + """
        self.current_order = []  # Xóa danh sách cũ

        # Thực đơn bên PHẢI
        self.menu_items = ["Bánh mì thịt", "Bánh mì trứng", "Bánh mì pate", 
                           "Bánh mì xíu mại", "Bánh mì chả cá"]

        self.menu_scroll = ScrollView(size_hint=(0.4, 0.6), pos_hint={"x": 0.55, "y": 0.3})
        self.menu_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.menu_layout.bind(minimum_height=self.menu_layout.setter('height'))

        for item in self.menu_items:
            btn = Button(text=item, size_hint_y=None, height=50, background_color=(0.2, 0.2, 0.2, 1))
            btn.bind(on_press=self.add_to_order)
            self.menu_layout.add_widget(btn)

        self.menu_scroll.add_widget(self.menu_layout)

        # Nút hoàn thành đơn hàng
        self.finish_order_btn = Button(
            text="Hoàn thành",
            size_hint=(0.2, 0.08),
            pos_hint={"x": 0.7, "y": 0.2},
        )
        self.finish_order_btn.bind(on_press=self.finish_order)

        # Thêm thực đơn vào layout
        self.layout.add_widget(self.menu_scroll)
        self.layout.add_widget(self.finish_order_btn)

    def add_to_order(self, instance):
        """ Thêm món vào đơn hàng """
        self.current_order.append(instance.text)
        instance.disabled = True  # Vô hiệu hóa món đã chọn

    def finish_order(self, instance):
        """ Hiển thị danh sách món đã chọn bên trái """
        if self.current_order:
            order_text = "Đơn hàng:\n" + "\n".join(self.current_order)
            order_label = Label(text=order_text, size_hint_y=None, height=100)
            self.orders_layout.add_widget(order_label)

        # Xóa menu sau khi hoàn thành
        self.layout.remove_widget(self.menu_scroll)
        self.layout.remove_widget(self.finish_order_btn)

class MyApp(MDApp):
    def build(self):
        return Makeorders()

if __name__ == "__main__":
    MyApp().run()
