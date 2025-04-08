import requests
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from kivymd.app import MDApp

class Revenue(Screen):
    def __init__(self, **kwargs):
        super(Revenue, self).__init__(**kwargs)

        self.period = 'day'
        self.active_period_btn = None

        # Background
        with self.canvas.before:
            Color(245/255, 177/255, 67/255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        # This handles dynamic font sizing for the table
        self.bind(size=self.update_table_font_sizes)

        self.main_layout = BoxLayout(orientation='vertical', spacing=5, padding=5)
        self.add_widget(self.main_layout)

        # Top bar with period buttons
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

        # Scroll area for displaying details
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.main_layout.add_widget(self.scroll_view)

        self.table_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.table_layout.bind(minimum_height=self.table_layout.setter('height'))
        self.scroll_view.add_widget(self.table_layout)

        # Label to show total
        self.total_label = Label(
            text="",
            size_hint_y=None,
            height='40dp',
            font_size='18sp',
            color=(0, 0, 0, 1)
        )
        self.main_layout.add_widget(self.total_label)

        # Default to 'day'
        self.select_period(day_btn, 'day')

    # -------------------------------------------------------------------------
    # 1) Refresh data manually if needed (e.g. from another screen).
    # -------------------------------------------------------------------------
    def refresh_data(self, period=None):
        if period:
            self.period = period
        self.display_revenue(self.period)

    # -------------------------------------------------------------------------
    # 2) Switch period (day/week/month/total) and re-fetch the relevant data
    # -------------------------------------------------------------------------
    def select_period(self, new_btn, period):
        # Update the button backgrounds
        if self.active_period_btn and self.active_period_btn != new_btn:
            self.active_period_btn.background_color = (233/255, 150/255, 14/255, 1)
        new_btn.background_color = (100/255, 200/255, 14/255, 1)
        self.active_period_btn = new_btn

        # Display new period
        self.display_revenue(period)

    def display_revenue(self, period):
        
        self.period = period
        self.table_layout.clear_widgets()

        # Build the microservice endpoint
        base_url = "http://localhost:8002/revenue"
        if period == 'day':
            url = f"{base_url}/daily"
        elif period == 'week':
            url = f"{base_url}/weekly"
        elif period == 'month':
            url = f"{base_url}/monthly"
        else:
            url = f"{base_url}/total"

        resp = requests.get(url)
        if resp.status_code != 200:
            print("Error fetching revenue:", resp.text)
            self.total_label.text = "Không có dữ liệu doanh thu"
            return

        data = resp.json()
        rows = data.get("rows", [])
        total_sum = data.get("total_sum", 0)
        if not rows:
            self.total_label.text = "Không có dữ liệu doanh thu"
            return

        def auto_height_boxlayout():
            rb = BoxLayout(orientation='horizontal', size_hint_y=None)
            rb.bind(minimum_height=rb.setter('height'))
            return rb

        if period == 'day':
            
            for row in rows:
                done_str = str(row.get("done_orders", ""))
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
                # autosize
                items_btn.bind(texture_size=lambda b, s: setattr(b, 'height', s[1] + 20))

                time_str = str(row.get("time", ""))
                time_btn = Button(
                    text=time_str,
                    size_hint=(0.15, 1),
                    background_color=(233/255, 150/255, 14/255, 1),
                    halign="center",
                    valign="middle"
                )
                time_btn.bind(size=lambda b, s: setattr(b, 'text_size', (s[0], None)))

                price_val = int(row.get("price", 0))
                price_str = self.format_money(price_val)
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

            self.total_label.text = f"Doanh thu hôm nay: {self.format_money(total_sum)} VND"

        elif period == 'week':
            # Suppose rows is a list of dicts, each with:
            # { "day_name_vi": "Thứ 2", "day": 28, "month": 8, "year": 2023, "price": 200000}
            for row_g in rows:
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

            self.total_label.text = f"Doanh thu tuần này: {self.format_money(total_sum)} VND"

        elif period == 'month':
            # rows might be { "day": 15, "month": 9, "year": 2023, "price": 400000 }
            for row_g in rows:
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

            self.total_label.text = f"Doanh thu tháng này: {self.format_money(total_sum)} VND"

        else:  # 'total'
            # rows might be { "year_month": "2023-08", "price": 1000000 }
            for row_g in rows:
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

            self.total_label.text = f"Tổng doanh thu: {self.format_money(total_sum)} VND"

        self.update_table_font_sizes()

    def get_label_for_period(self, period):
        if period == 'day':
            return "Doanh thu hôm nay"
        elif period == 'week':
            return "Doanh thu tuần này"
        elif period == 'month':
            return "Doanh thu tháng này"
        else:
            return "Tổng doanh thu"

    def format_money(self, value):
        s = f"{int(value):,}"
        return s.replace(",", ".")

    # -------------------------------------------------------------------------
    # 3c) Implement fetch_revenue_data
    # -------------------------------------------------------------------------
    def fetch_revenue_data(self, period):
        base_url = "http://localhost:8002/revenue"  # or wherever your service is
        if period == 'day':
            url = f"{base_url}/daily"
        elif period == 'week':
            url = f"{base_url}/weekly"
        elif period == 'month':
            url = f"{base_url}/monthly"
        else:
            url = f"{base_url}/total"
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                return resp.json()  # a dict with e.g. { "daily_revenue":..., "details": [...] }
            else:
                print("Error fetching revenue:", resp.text)
                return {}
        except Exception as e:
            print("Exception calling revenue service:", e)
            return {}

    # -------------------------------------------------------------------------
    # 4) Display logic for each period's "details" data
    # -------------------------------------------------------------------------
    def display_day_details(self, details):
        """
        Example structure for `details` might be:
        [
          {
            "done_orders": "Pizza x1, Coke x2",
            "time": "13:14",
            "price": 80000,
            "date": "2023-08-28"  # optional
          },
          ...
        ]
        We replicate your old row building logic using each order item.
        """
        for row in details:
            done_str = str(row.get("done_orders", ""))
            items_list = done_str.split(", ")
            items_text = "\n".join(items_list)

            row_box = self.auto_height_boxlayout()

            # "items_btn"
            items_btn = Button(
                text=items_text,
                size_hint=(0.65, None),
                background_color=(233/255, 150/255, 14/255, 1),
                halign="left",
                valign="middle",
                text_size=(220, None)
            )
            items_btn.bind(texture_size=lambda b, s: setattr(b, 'height', s[1] + 20))

            # "time_btn"
            time_btn = Button(
                text=str(row.get("time", "")),
                size_hint=(0.15, 1),
                background_color=(233/255, 150/255, 14/255, 1),
                halign="center",
                valign="middle"
            )
            time_btn.bind(size=lambda b, s: setattr(b, 'text_size', (s[0], None)))

            # "price_btn"
            price = row.get("price", 0)
            price_str = self.format_money(price)
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

    def display_week_details(self, details):
        """
        Suppose the microservice already aggregates by day. 
        `details` might be something like:
        [
          { "day_name_vi": "Thứ 2", "day": 28, "month": 8, "year": 2023, "price": 150000 },
          ...
        ]
        We'll replicate your old grouping logic or just show the data directly.
        """
        total_sum = 0
        for row_g in details:
            row_box = self.auto_height_boxlayout()

            # "left_btn"
            left_text = f"{row_g['day_name_vi']} {row_g['day']}/{row_g['month']}/{row_g['year']}"
            left_btn = Button(
                text=left_text,
                size_hint=(0.5, 1),
                background_color=(233/255, 150/255, 14/255, 1),
                halign="center",
                valign="middle"
            )
            left_btn.bind(size=lambda b, s: setattr(b, 'text_size', (s[0], None)))

            # "right_btn"
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

    def display_month_details(self, details):
        """
        Possibly `details` is like:
        [
          { "day": 28, "month": 8, "year": 2023, "price": 200000 },
          ...
        ]
        """
        for row_g in details:
            row_box = self.auto_height_boxlayout()

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

    def display_total_details(self, details):
        """
        Possibly `details` is like:
        [
          { "year_month": "2023-08", "price": 1500000 },
          ...
        ]
        """
        for row_g in details:
            row_box = self.auto_height_boxlayout()

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

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    def auto_height_boxlayout(self):
        rb = BoxLayout(orientation='horizontal', size_hint_y=None)
        rb.bind(minimum_height=rb.setter('height'))
        return rb


    def update_table_font_sizes(self, *args):
        """
        Recalculate font sizes for each row, the total label, and period buttons.
        """
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
