from frontend.roundButton import RoundedButton
from backend.foodmanager import FoodManager
from backend.cartmanager import CartManager
from backend.orderinfomanager import OrderInfoManager
import os

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen, ScreenManager, FallOutTransition
from kivy.graphics import Color, Rectangle
from kivymd.uix.button import MDIconButton
from kivymd.app import MDApp
from kivy.uix.popup import Popup


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.food_manager = FoodManager()
        self.cart_manager = CartManager()
        self.menu_items = self.food_manager.menu_items
        self.selected_quantities = {item['name']: 0 for item in self.menu_items}
        self.quantity_inputs = {}

        self.layout = FloatLayout()
        self.scroll_view = ScrollView(size_hint=(0.98, 0.8), pos_hint={"center_x": 0.5, "center_y": 0.55})

        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll_view.add_widget(self.container)
        self.layout.add_widget(self.scroll_view)

        # Add the confirm button
        self.confirm_button = RoundedButton(
            text="Thêm vào giỏ hàng",
            size_hint=(None, None),
            size=(250, 50),
            pos_hint={"center_x": 0.5, "y": 0.02},
            font_size=18
        )
        self.confirm_button.change_color(0.9, 0.4, 0.1, 1)
        self.confirm_button.color=(0,0,0,1)
        self.confirm_button.bind(on_press=self.save_to_cart)
        self.layout.add_widget(self.confirm_button)

        self.add_widget(self.layout)
        self.populate_menu()

    def populate_menu(self):
        for item in self.menu_items:
            name = item['name']
            price = item['price']
            image_path = item['image']
            if not os.path.exists(image_path):
                image_path = 'images/default.png'

            row_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=100)

            image = Image(source=image_path, size_hint=(0.2, 1))

            info_container = BoxLayout(orientation='vertical', size_hint=(0.4, 1), padding=5, spacing=2)
            with info_container.canvas.before:
                Color(245 / 255, 177 / 255, 67 / 255, 1)
                info_container.bg_rect = Rectangle(size=info_container.size, pos=info_container.pos)
            info_container.bind(size=self.update_bg_rect, pos=self.update_bg_rect)

            name_label = Label(text=f"{name}", size_hint=(1, 0.5), color=(0, 0, 0, 1), halign="left", valign="middle")
            price_label = Label(text=f"Giá: {price}đ", size_hint=(1, 0.5), color=(0, 0, 0, 1), halign="left", valign="middle")
            for lbl in [name_label, price_label]:
                lbl.bind(size=lbl.setter('text_size'))
                lbl.text_size = lbl.size
            info_container.add_widget(name_label)
            info_container.add_widget(price_label)

            control_box = BoxLayout(size_hint=(0.4, 1), spacing=5)
            minus_btn = Button(text="-", size_hint=(0.2, 1), background_color=(200 / 255, 50 / 255, 50 / 255, 1), color=(1, 1, 1, 1))
            quantity_input = TextInput(
                text="0",
                size_hint=(0.3, 1),
                multiline=False,
                halign="center"
            )
            quantity_input.bind(text=self.make_quantity_update_handler(name))
            quantity_input.bind(minimum_height=lambda instance, value: setattr(instance, 'padding', [0, (instance.height - instance.line_height) / 2]))
            self.quantity_inputs[name] = quantity_input

            plus_btn = Button(text="+", size_hint=(0.2, 1), background_color=(200 / 255, 50 / 255, 50 / 255, 1), color=(1, 1, 1, 1))

            minus_btn.bind(on_press=self.make_decrement_handler(name, quantity_input))
            plus_btn.bind(on_press=self.make_increment_handler(name, quantity_input))

            control_box.add_widget(minus_btn)
            control_box.add_widget(quantity_input)
            control_box.add_widget(plus_btn)

            row_box.add_widget(image)
            row_box.add_widget(info_container)
            row_box.add_widget(control_box)

            self.container.add_widget(row_box)

    def update_bg_rect(self, instance, value):
        instance.bg_rect.pos = instance.pos
        instance.bg_rect.size = instance.size
    def make_quantity_update_handler(self, name):
        def update_quantity(instance, value):
            try:
                quantity = max(0, int(value))
            except ValueError:
                quantity = 0
            self.selected_quantities[name] = quantity
        return update_quantity

    def increment(self, item, input_field):
        self.selected_quantities[item] += 1
        input_field.text = str(self.selected_quantities[item])

    def decrement(self, item, input_field):
        if self.selected_quantities[item] > 0:
            self.selected_quantities[item] -= 1
            input_field.text = str(self.selected_quantities[item])
    def make_increment_handler(self, name, input_field):
        return lambda btn: self.increment(name, input_field)

    def make_decrement_handler(self, name, input_field):
        return lambda btn: self.decrement(name, input_field)

    def save_to_cart(self, instance):
        self.cart_manager.write_cart(self.selected_quantities, self.menu_items)
        # Reset all quantities
        check=False
        for name in self.selected_quantities:
            if self.selected_quantities[name] != 0:
                check=True
                break
        for name in self.selected_quantities:
            self.selected_quantities[name] = 0
            if name in self.quantity_inputs:
                self.quantity_inputs[name].text = "0"
        if check==True:
            self.show_popup("Đã thêm vào giỏ hàng!")
        else:
            self.show_popup("Bạn chưa chọn gì!")
    def show_popup(self, message):
        popup = Popup(
            title="Thông báo",
            content=Label(text=message),
            size_hint=(None, None),
            size=(300, 150),
            auto_dismiss=True
        )
        popup.open()

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos


class CartScreen(Screen):
    def __init__(self, **kwargs):
        super(CartScreen, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.layout = FloatLayout()
        self.scroll = ScrollView(size_hint=(0.98, 0.82), pos_hint={"center_x": 0.5, "center_y": 0.55})

        self.container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=10,
            padding=10
        )
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container)

        self.buy_all_button = RoundedButton(
            text="Mua tất cả",
            size_hint=(None, None),
            size=(250, 50),
            pos_hint={"center_x": 0.5, "y": 0.02},
            font_size=18
        )
        self.buy_all_button.change_color(0.9, 0.4, 0.1, 1)
        self.buy_all_button.bind(on_press=self.handle_buy_all)

        self.layout.add_widget(self.scroll)
        self.layout.add_widget(self.buy_all_button)
        self.add_widget(self.layout)

        self.load_cart()

    def load_cart(self):
        self.container.clear_widgets()
        
        cart = CartManager().read_cart()
        if cart.empty:
            no_order_label = Label(
                text="Bạn không có gì trong giỏ hàng",
                color=(0, 0, 0, 1),
                font_size=18,
                size_hint=(1, None),
                height=40
            )
            self.container.add_widget(no_order_label)
            return

        for _, row in cart.iterrows():
            order_info = str(row['order']).replace(",", "\n")
            order_info = ' ' + order_info
            total_price = str(row['price'])

            order_box = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                padding=5,
                spacing=5
            )
            order_box.height = 110 + (order_info.count('\n') * 18)

            top_row = BoxLayout(size_hint_y=0.6, spacing=10)

            order_btn = RoundedButton(
                text=order_info,
                size_hint=(0.7, 1),
                halign="left",
                valign="middle",
                text_size=(None, None)
            )
            order_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            order_btn.color=(0, 0, 0, 1)
            order_btn.bind(texture_size=order_btn.setter("size"))

            price_btn = RoundedButton(
                text=f"{total_price}đ",
                size_hint=(0.3, 1)
            )
            price_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            price_btn.color=(0, 0, 0, 1)

            mua_btn = Button(
                text="Mua",
                size_hint=(1, None),
                height=50,
                background_color=(233 / 255, 150 / 255, 14 / 255, 1),
                color=(0, 0, 0, 1),
            )
            mua_btn.bind(on_press=lambda instance, o=row['order'], p=row['price']: self.show_order_popup(o, p, mua_tat_ca=False, single_order_row=row))

            top_row.add_widget(order_btn)
            top_row.add_widget(price_btn)
            order_box.add_widget(top_row)
            order_box.add_widget(mua_btn)

            self.container.add_widget(order_box)

    def handle_buy_all(self, instance):
        cart = CartManager().read_cart()

        if cart.empty:
            self.show_warning("Không có đơn hàng nào trong giỏ.")
            return

        combined_order = []
        total_price = 0

        for _, row in cart.iterrows():
            combined_order.append(str(row['order']))
            total_price += float(row['price'])

        full_order_text = ", ".join(combined_order)
        self.show_order_popup(full_order_text, total_price, mua_tat_ca=True)

    def show_order_popup(self, order, price, mua_tat_ca=False, single_order_row=None):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        name_input = TextInput(hint_text="Họ tên", size_hint_y=None, height=40)
        phone_input = TextInput(hint_text="Số điện thoại", size_hint_y=None, height=40)
        address_input = TextInput(hint_text="Địa chỉ", size_hint_y=None, height=40)
        note_input = TextInput(hint_text="Ghi chú", size_hint_y=None, height=60)

        confirm_button = Button(
            text="Xác nhận",
            size_hint=(1, None),
            height=50,
            background_color=(0.2, 0.6, 0.2, 1),
            color=(1, 1, 1, 1)
        )

        content.add_widget(name_input)
        content.add_widget(phone_input)
        content.add_widget(address_input)
        content.add_widget(note_input)
        content.add_widget(confirm_button)

        popup = Popup(
            title="Thông tin đơn hàng",
            content=content,
            size_hint=(None, None),
            size=(400, 450),
            auto_dismiss=True
        )

        confirm_button.bind(
            on_press=lambda x: self.confirm_order(
                popup,
                name_input.text,
                phone_input.text,
                address_input.text,
                note_input.text,
                order,
                price,
                mua_tat_ca,
                single_order_row
            )
        )

        popup.open()
    
    def confirm_order(self, popup, name, phone, address, note, order, price, mua_tat_ca=False, single_order_row=None):
        if not name.strip() or not phone.strip() or not address.strip():
            self.show_warning("Vui lòng điền đầy đủ họ tên, số điện thoại và địa chỉ.")
            return

        if not phone.strip().isdigit() or len(phone.strip()) < 8:
            self.show_warning("Số điện thoại không hợp lệ. Vui lòng nhập ít nhất 8 chữ số.")
            return

        popup.dismiss()
        OrderInfoManager().save_order_info(name, phone, address, note, order, price)

        if mua_tat_ca:
            CartManager().clear_cart()
        elif single_order_row is not None:
            CartManager().delete_order(order, price)
        self.load_cart()


    def show_warning(self, message):
        warning = Popup(
            title="Lỗi",
            content=Label(text=message),
            size_hint=(None, None),
            size=(350, 200)
        )
        warning.open()

    def on_pre_enter(self, *args):
        self.load_cart()

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

class OrderScreen(Screen):
    def __init__(self, **kwargs):
        super(OrderScreen, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.layout = FloatLayout()
        self.scroll = ScrollView(size_hint=(0.98, 0.92), pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.container.bind(minimum_height=self.container.setter('height'))

        self.scroll.add_widget(self.container)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

        self.order_manager = OrderInfoManager()
        self.load_orders()

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def load_orders(self):
        self.container.clear_widgets()
        df = self.order_manager.read_orders()

        if df.empty:
            no_order_label = Label(
                text="Bạn không có đơn hàng nào",
                font_size=18,
                color=(0, 0, 0, 1),
                size_hint=(1, None),
                height=40
            )
            self.container.add_widget(no_order_label)
            return

        for idx, row in df.iterrows():
            order_text = str(row.get("order", "")).replace(",", "\n").strip()
            order_text= ' ' + order_text
            price = str(row.get("price", ""))

            order_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5, padding=5)

            top_row = BoxLayout(size_hint_y=None, spacing=10)

            order_btn = Button(
                text=order_text,
                size_hint=(0.7, None),
                halign="left",
                valign="middle",
                text_size=(None , None),  
                color=(0, 0, 0, 1)
            )

            # Force update to get correct texture size
            order_btn.texture_update()
            height = order_btn.texture_size[1] + 20
            order_btn.height = height

            price_btn = Button(
                text=f"{price}đ",
                size_hint=(0.3, None),
                height=height,
                color=(0, 0, 0, 1)
            )

            top_row.height = height
            top_row.add_widget(order_btn)
            top_row.add_widget(price_btn)

            change_btn = Button(
                text="Thay đổi thông tin",
                size_hint_y=None,
                height=40,
                background_color=(0.1, 0.3, 0.6, 1),
                color=(1, 1, 1, 1)
            )
            delete_btn = Button(
                text="Hủy đơn",
                size_hint_y=None,
                height=40,
                background_color=(0.7, 0.2, 0.2, 1),
                color=(1, 1, 1, 1)
            )

            change_btn.bind(on_press=lambda _, i=idx, r=row: self.show_edit_popup(i, r))
            delete_btn.bind(on_press=lambda _, i=idx: self.delete_order(i))

            order_box.add_widget(top_row)
            order_box.add_widget(change_btn)
            order_box.add_widget(delete_btn)

            # Let layout decide height after components are added
            order_box.height = height + 40 + 40 + 20
            self.container.add_widget(order_box)

    def show_edit_popup(self, index, row):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        name_input = TextInput(text=str(row.get("name", "")), hint_text="Họ tên", size_hint_y=None, height=40)
        phone_input = TextInput(text=str(row.get("phone", "")), hint_text="Số điện thoại", size_hint_y=None, height=40)
        address_input = TextInput(text=str(row.get("address", "")), hint_text="Địa chỉ", size_hint_y=None, height=40)
        note_input = TextInput(text=str(row.get("note", "")), hint_text="Ghi chú", size_hint_y=None, height=60)

        confirm_button = Button(
            text="Xác nhận",
            size_hint=(1, None),
            height=50,
            background_color=(0.2, 0.6, 0.2, 1),
            color=(1, 1, 1, 1)
        )

        content.add_widget(name_input)
        content.add_widget(phone_input)
        content.add_widget(address_input)
        content.add_widget(note_input)
        content.add_widget(confirm_button)

        popup = Popup(
            title="Chỉnh sửa đơn hàng",
            content=content,
            size_hint=(None, None),
            size=(400, 450),
            auto_dismiss=True
        )

        confirm_button.bind(
            on_press=lambda _: self.update_order(index, name_input.text, phone_input.text, address_input.text, note_input.text, popup)
        )

        popup.open()

    def update_order(self, index, name, phone, address, note, popup):
        self.order_manager.update_order(index, name, phone, address, note)
        popup.dismiss()
        self.load_orders()

    def delete_order(self, index):
        self.order_manager.delete_order(index)
        self.load_orders()
    def on_pre_enter(self, *args):
        self.load_orders()

class HistoryScreen(Screen):
    pass

class MainScreenCus(Screen):
    def __init__(self, **kwargs):
        super(MainScreenCus, self).__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.active_tab = None

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
            size_hint=(0.4, 1)
        )
        self.greeting_label.bind(size=self.greeting_label.setter('text_size'))
        self.bind(size=self.update_font_size)

        settings_button = MDIconButton(
            icon="cog",
            md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1),
            icon_size="20sp",
        )

        top_bar.add_widget(self.greeting_label)
        top_bar.add_widget(settings_button)

        tab_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='40dp'
        )

        self.tabs = [
            ("Menu", "menu_screen"),
            ("Giỏ hàng", "cart_screen"),
            ("Đơn hàng", "order_screen"),
            ("Lịch sử", "history_screen")
        ]

        self.buttons = []
        for text, screen_name in self.tabs:
            btn = RoundedButton(
                text=text,
                size_hint=(0.25, 1),
                font_size=(self.width + self.height)/2 / 20,
            )
            btn.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            btn.color=(0,0,0,1)
            btn.bind(on_press=lambda b, sn=screen_name: self.select_tab(b, sn))
            self.buttons.append(btn)
            tab_bar.add_widget(btn)

        self.bind(size=self.update_button_font_size)

        self.screen_manager = ScreenManager(transition=FallOutTransition())
        self.screen_manager.add_widget(MenuScreen(name="menu_screen"))
        self.screen_manager.add_widget(CartScreen(name="cart_screen"))
        self.screen_manager.add_widget(OrderScreen(name="order_screen"))
        self.screen_manager.add_widget(HistoryScreen(name="history_screen"))

        root.add_widget(top_bar)
        root.add_widget(tab_bar)
        root.add_widget(self.screen_manager)
        self.add_widget(root)

        if self.buttons:
            self.select_tab(self.buttons[0], "menu_screen")

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
        self.greeting_label.font_size = (self.width + self.height)/2 / 25

    def update_button_font_size(self, *args):
        for btn in self.buttons:
            btn.font_size = (self.width + self.height)/2 / 36
