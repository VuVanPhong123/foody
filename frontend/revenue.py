from backend.revenuemanager import RevenueManager
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from kivymd.app import MDApp
import pandas as pd

class Revenue(Screen):
    def __init__(self, **kwargs):
        super(Revenue, self).__init__(**kwargs)
        self.revenue_manager = RevenueManager()
        self.period = 'day'
        self.active_period_btn = None

        with self.canvas.before:
            Color(245/255, 177/255, 67/255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.bind(size=self.update_table_font_sizes)

        self.main_layout = BoxLayout(orientation='vertical', spacing=5, padding=5)
        self.add_widget(self.main_layout)

        self.period_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing=5)
        self.main_layout.add_widget(self.period_bar)

        day_btn = Button(text="Ngày", background_color=(233/255, 150/255, 14/255, 1))
        week_btn = Button(text="Tuần", background_color=(233/255, 150/255, 14/255, 1))
        month_btn = Button(text="Tháng", background_color=(233/255, 150/255, 14/255, 1))
        total_btn = Button(text="Tổng", background_color=(233/255, 150/255, 14/255, 1))

        day_btn.bind(on_press=lambda x: self.select_period(day_btn, 'day'))
        week_btn.bind(on_press=lambda x: self.select_period(week_btn, 'week'))
        month_btn.bind(on_press=lambda x: self.select_period(month_btn, 'month'))
        total_btn.bind(on_press=lambda x: self.select_period(total_btn, 'total'))

        self.period_bar.add_widget(day_btn)
        self.period_bar.add_widget(week_btn)
        self.period_bar.add_widget(month_btn)
        self.period_bar.add_widget(total_btn)
        self.period_buttons = [day_btn, week_btn, month_btn, total_btn]
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.main_layout.add_widget(self.scroll_view)

        self.table_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.table_layout.bind(minimum_height=self.table_layout.setter('height'))
        self.scroll_view.add_widget(self.table_layout)

        self.total_label = Label(
            text="",
            size_hint_y=None,
            height='40dp',
            font_size='18sp',
            color=(0, 0, 0, 1)
        )
        self.main_layout.add_widget(self.total_label)
        self.select_period(day_btn, 'day')

    def refresh_data(self, period=None):
        self.revenue_manager.revenue_data = self.revenue_manager.load_revenue_data()
        if period:
            self.period = period
        self.display_revenue(self.period)

    def format_money(self, value):
        s = f"{int(value):,}"
        return s.replace(",", ".")
    def select_period(self, new_btn, period):

        if self.active_period_btn and self.active_period_btn != new_btn:
            self.active_period_btn.background_color = (233/255, 150/255, 14/255, 1)
        new_btn.background_color = (100/255, 200/255, 14/255, 1)
        self.active_period_btn = new_btn

        self.display_revenue(period)

    def display_revenue(self, period):
        self.period = period
        self.table_layout.clear_widgets()

        df = self.revenue_manager.get_revenue_by_period(period)
        if df.empty:
            self.total_label.text = "Không có dữ liệu doanh thu"
            return

        def auto_height_boxlayout():
            rb = BoxLayout(orientation='horizontal', size_hint_y=None)
            rb.bind(minimum_height=rb.setter('height'))
            return rb

        if period == 'day':
            total_sum = 0
            for _, row in df.iterrows():
                done_str = str(row['done_orders'])
                items_list = done_str.split(", ")
                items_text = "\n".join(items_list)

                row_box = auto_height_boxlayout()
                items_btn = Button(
                    text=items_text,
                    size_hint=(0.65, None),
                    background_color=(233/255, 150/255, 14/255, 1),
                    halign="left",
                    valign="middle",
                    text_size=(220, None)
                )
                items_btn.bind(texture_size=lambda b, s: setattr(b, 'height', s[1] + 20))

                time_btn = Button(
                    text=str(row['time']),
                    size_hint=(0.15, 1),
                    background_color=(233/255, 150/255, 14/255, 1),
                    halign="center",
                    valign="middle"
                )
                time_btn.bind(size=lambda b, s: setattr(b, 'text_size', (s[0], None)))

                price_str = self.format_money(row['price'])
                price_btn = Button(
                    text=price_str,
                    size_hint=(0.2, 1),
                    background_color=(233/255, 150/255, 14/255, 1),
                    halign="center",
                    valign="middle"
                )
                price_btn.bind(size=lambda b, s: setattr(b, 'text_size', (s[0], None)))

                row_box.add_widget(items_btn)
                row_box.add_widget(time_btn)
                row_box.add_widget(price_btn)
                self.table_layout.add_widget(row_box)

                total_sum += row['price']

            self.total_label.text = f"Doanh thu hôm nay: {self.format_money(total_sum)} VND"

        elif period == 'week':
            df['date_only'] = df['date'].dt.normalize()
            df['day'] = df['date_only'].dt.day
            df['month'] = df['date_only'].dt.month
            df['year'] = df['date_only'].dt.year
            df['day_name_en'] = df['date_only'].dt.day_name()
            en2vi = {
                "Monday": "Thứ 2",
                "Tuesday": "Thứ 3",
                "Wednesday": "Thứ 4",
                "Thursday": "Thứ 5",
                "Friday": "Thứ 6",
                "Saturday": "Thứ 7",
                "Sunday": "Chủ Nhật"
            }
            df['day_name_vi'] = df['day_name_en'].map(en2vi)

            grouped = df.groupby(['date_only','day','month','year','day_name_vi'])['price'].sum().reset_index()
            total_sum = 0
            for _, row_g in grouped.iterrows():
                row_box = auto_height_boxlayout()

                left_text = f"{row_g['day_name_vi']} {row_g['day']}/{row_g['month']}/{row_g['year']}"
                left_btn = Button(
                    text=left_text,
                    size_hint=(0.5, 1),
                    background_color=(233/255, 150/255, 14/255, 1),
                    halign="center",
                    valign="middle"
                )
                left_btn.bind(size=lambda b, s: setattr(b, 'text_size', (s[0], None)))

                price_str = self.format_money(row_g['price'])
                right_btn = Button(
                    text=price_str,
                    size_hint=(0.5, 1),
                    background_color=(233/255, 150/255, 14/255, 1),
                    halign="center",
                    valign="middle"
                )
                right_btn.bind(size=lambda b, s: setattr(b, 'text_size', (s[0], None)))

                row_box.add_widget(left_btn)
                row_box.add_widget(right_btn)
                self.table_layout.add_widget(row_box)
                total_sum += row_g['price']

            self.total_label.text = f"Doanh thu tuần này: {self.format_money(total_sum)} VND"

        elif period == 'month':
            df['date_only'] = df['date'].dt.normalize()
            df['day'] = df['date_only'].dt.day
            df['month'] = df['date_only'].dt.month
            df['year'] = df['date_only'].dt.year

            grouped = df.groupby(['year','month','day'])['price'].sum().reset_index()
            total_sum = 0
            for _, row_g in grouped.iterrows():
                row_box = auto_height_boxlayout()

                left_text = f"Ngày {row_g['day']}/{row_g['month']}/{row_g['year']}"
                left_btn = Button(
                    text=left_text,
                    size_hint=(0.5, 1),
                    background_color=(233/255, 150/255, 14/255, 1),
                    halign="center",
                    valign="middle"
                )
                left_btn.bind(size=lambda b, s: setattr(b, 'text_size', (s[0], None)))

                price_str = self.format_money(row_g['price'])
                right_btn = Button(
                    text=price_str,
                    size_hint=(0.5, 1),
                    background_color=(233/255, 150/255, 14/255, 1),
                    halign="center",
                    valign="middle"
                )
                right_btn.bind(size=lambda b, s: setattr(b, 'text_size', (s[0], None)))

                row_box.add_widget(left_btn)
                row_box.add_widget(right_btn)
                self.table_layout.add_widget(row_box)
                total_sum += row_g['price']

            self.total_label.text = f"Doanh thu tháng này: {self.format_money(total_sum)} VND"

        else:  # 'total'
            df['year_month'] = df['date'].dt.strftime('%Y-%m')
            grouped = df.groupby('year_month')['price'].sum().reset_index()
            total_sum = 0
            for _, row_g in grouped.iterrows():
                row_box = auto_height_boxlayout()

                ym_btn = Button(
                    text=row_g['year_month'],
                    size_hint=(0.5, 1),
                    background_color=(233/255, 150/255, 14/255, 1),
                    halign="center",
                    valign="middle"
                )
                ym_btn.bind(size=lambda b, s: setattr(b, 'text_size', (s[0], None)))

                price_str = self.format_money(row_g['price'])
                price_btn = Button(
                    text=price_str,
                    size_hint=(0.5, 1),
                    background_color=(233/255, 150/255, 14/255, 1),
                    halign="center",
                    valign="middle"
                )
                price_btn.bind(size=lambda b, s: setattr(b, 'text_size', (s[0], None)))

                row_box.add_widget(ym_btn)
                row_box.add_widget(price_btn)
                self.table_layout.add_widget(row_box)
                total_sum += row_g['price']

            self.total_label.text = f"Tổng doanh thu: {self.format_money(total_sum)} VND"
        self.update_table_font_sizes()

    def update_table_font_sizes(self, *args):
        multiplier = 0.02
        for row_box in self.table_layout.children:
            for btn in row_box.children:
                btn.font_size = (self.width+2*self.height)/2 * multiplier
        self.total_label.font_size = str(int((self.width+2*self.height)/2 * 0.018)) + 'sp'
        for btn in self.period_buttons:
            btn.font_size = (self.width+2*self.height)/2 * 0.018

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos


class DemoRevenueApp(MDApp):
    def build(self):
        return Revenue()

if __name__ == '__main__':
    DemoRevenueApp().run()
