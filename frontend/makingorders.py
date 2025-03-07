from frontend.roundButton import RoundedButton
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from kivymd.app import MDApp

class Makingorders(Screen):
    def __init__(self, **kwargs):
        super(Makingorders, self).__init__(**kwargs)
        with self.canvas.before:
            Color(245/255, 177/255, 67/255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)
        
        # Nút "+" để hiển thị menu
        self.create_order_btn = RoundedButton(
            text="+", size_hint=(0.1, 0.07), font_size=15,
            pos_hint={"center_x": 0.1, "center_y": 0.1})
        self.create_order_btn.change_color(233/255, 150/255, 14/255, 1)
        self.create_order_btn.bind(on_press=self.toggle_menu)
        self.add_widget(self.create_order_btn)
        
        # Layout chứa menu và nút hoàn thành
        self.layout = FloatLayout()
        self.menu_items = {}
        self.orders = []

        # ScrollView cho menu
        self.scroll_view = ScrollView(size_hint=(0.4, 0.5), pos_hint={"center_x": 0.7, "center_y": 0.5})
        self.menu_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.menu_layout.bind(minimum_height=self.menu_layout.setter('height'))
        
        items = ["Bánh mì thịt", "Bánh mì trứng", "Bánh mì pate", "Bánh mì xíu mại", "Bánh mì chả cá"]
        for item in items:
            self.menu_items[item] = 0
            btn = Button(text=item, size_hint_y=None, height=50)
            btn.bind(on_press=self.add_to_order)
            self.menu_layout.add_widget(btn)
        
        self.scroll_view.add_widget(self.menu_layout)

        # Nút "Hoàn thành"
        self.complete_btn = Button(
            text="Hoàn thành", size_hint=(0.4, 0.1), pos_hint={"center_x": 0.7, "center_y": 0.2})
        self.complete_btn.bind(on_press=self.complete_order)

        # ScrollView cho danh sách đơn hàng
        self.scroll_view2 = ScrollView(size_hint=(0.8, 0.7), pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.order_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.order_layout.bind(minimum_height=self.order_layout.setter('height'))
        self.scroll_view2.add_widget(self.order_layout)
        
        # Nhãn thông báo khi không có đơn hàng nào
        self.no_orders_label = Label(text="Bạn chưa có đơn hàng nào", size_hint_y=None, height=50)
        self.order_layout.add_widget(self.no_orders_label)
        
        self.layout.add_widget(self.scroll_view2)
        self.add_widget(self.layout)
        
    def toggle_menu(self, instance):
        """Hiện/Ẩn menu và nút hoàn thành"""
        if self.scroll_view.parent:
            self.layout.remove_widget(self.scroll_view)
            self.layout.remove_widget(self.complete_btn)
        else:
            self.layout.add_widget(self.scroll_view)
            self.layout.add_widget(self.complete_btn)
            self.menu_items = {item: 0 for item in self.menu_items}  # Reset menu selection

    def add_to_order(self, instance):
        """Thêm món vào đơn hàng"""
        item = instance.text
        self.menu_items[item] += 1

    def complete_order(self, instance):
        """Tạo đơn hàng mới và hiển thị"""
        if any(qty > 0 for qty in self.menu_items.values()):
            if self.no_orders_label.parent:
                self.order_layout.remove_widget(self.no_orders_label)

            order_text = f"Đơn hàng {len(self.orders) + 1}:\n"
            order_text += '\n'.join(f"{item} x{qty}" for item, qty in self.menu_items.items() if qty > 0)
            self.orders.append(order_text)
            
            num_lines = order_text.count('\n') + 1
            button_height = max(50, num_lines * 25)
            
            order_btn = Button(text=order_text, size_hint_y=None, height=button_height)
            complete_btn = Button(text="Xong", size_hint=(0.2, None), height=button_height)
            cancel_btn = Button(text="Hủy", size_hint=(0.2, None), height=button_height)
            
            order_box = BoxLayout(size_hint_y=None, height=button_height)
            order_box.add_widget(complete_btn)
            order_box.add_widget(cancel_btn)
            order_box.add_widget(order_btn)
            
            complete_btn.bind(on_press=lambda x: self.remove_order(order_box))
            cancel_btn.bind(on_press=lambda x: self.remove_order(order_box))
            
            self.order_layout.add_widget(order_box)
        
        self.toggle_menu(None)  # Ẩn menu sau khi hoàn thành đơn

    def remove_order(self, order_widget):
        """Xóa đơn hàng khi bấm nút hoàn thành hoặc hủy"""
        self.order_layout.remove_widget(order_widget)
        if len(self.order_layout.children) == 0:
            self.order_layout.add_widget(self.no_orders_label)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

class app(MDApp):
    def build(self):
        return Makingorders()

if __name__ == '__main__':
    app().run()
