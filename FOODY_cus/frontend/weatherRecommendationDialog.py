from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivymd.uix.spinner import MDSpinner
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
import threading
import re
from services.recommendation_service import RecommendationService

# Centralized color palette
COLORS = {
    'primary': (233/255, 150/255, 14/255, 0.3),  # Weather box background
    'text': (0, 0, 0, 1),  # Black text
    'weather_desc': (0, 0.6, 0.8, 1),  # Blue for weather description
    'temperature': (1, 0.34, 0.13, 1),  # Orange for temperature
    'humidity': (0.3, 0.69, 0.31, 1),  # Green for humidity
    'item_bg': (1, 1, 1, 0.8),  # White for item background
    'summary_bg': (250/255, 243/255, 224/255, 1),  # Light orange for summary
    'error': (0.96, 0.27, 0.21, 1),  # Red for errors
}

class WeatherRecommendationDialog(ModalView):
    def __init__(self, menu_items, add_to_cart_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.8)
        self.menu_items = menu_items
        self.add_to_cart_callback = add_to_cart_callback
        self.recommendation_service = RecommendationService()
        self.scheduled_events = []  # Track scheduled Clock events
        self.is_loading = False  # Track loading state

        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        self.add_widget(self.layout)

        # Header
        self.header = Label(
            text="Đề xuất món ăn dựa trên thời tiết",
            size_hint_y=None,
            height=dp(40),
            font_size=dp(18),
            bold=True,
            color=COLORS['item_bg']
        )
        self.layout.add_widget(self.header)

        # Weather info
        weather_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(80),
            padding=dp(10)
        )
        with weather_box.canvas.before:
            Color(*COLORS['primary'])
            self.weather_bg = Rectangle(size=weather_box.size, pos=weather_box.pos)
        weather_box.bind(size=self._update_rect, pos=self._update_rect)

        self.weather_info = Label(
            text="Loading weather data...",
            halign='center',
            valign='middle',
            markup=True,
            color=COLORS['text']
        )
        self.weather_info.bind(width=lambda *x: setattr(self.weather_info, 'text_size', (self.weather_info.width, None)))
        weather_box.add_widget(self.weather_info)
        self.layout.add_widget(weather_box)

        # Recommendations scroll view
        self.scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(8)
        )
        self.recommendations_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=dp(10),
            spacing=dp(10)
        )
        self.recommendations_container.bind(minimum_height=self.recommendations_container.setter('height'))
        self.scroll.add_widget(self.recommendations_container)
        self.layout.add_widget(self.scroll)

        # Loading spinner
        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(46), dp(46)),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        # Bottom buttons
        buttons_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        self.refresh_btn = Button(
            text="Refresh",
            size_hint_x=0.5,
            background_color=(0.3, 0.7, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        self.refresh_btn.bind(on_press=self.load_recommendations)

        self.close_btn = Button(
            text="Close",
            size_hint_x=0.5,
            background_color=(0.7, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        self.close_btn.bind(on_press=self.dismiss)

        buttons_layout.add_widget(self.refresh_btn)
        buttons_layout.add_widget(self.close_btn)
        self.layout.add_widget(buttons_layout)

    def _update_rect(self, instance, value):
        self.weather_bg.pos = instance.pos
        self.weather_bg.size = instance.size

    def on_open(self):
        Clock.schedule_once(self.load_recommendations, 0.1)

    def load_recommendations(self, *args):
        if self.is_loading:
            return
        self.is_loading = True
        self.refresh_btn.disabled = True

        self.recommendations_container.clear_widgets()
        if self.spinner not in self.layout.children:
            self.layout.add_widget(self.spinner)

        threading.Thread(target=self._load_recommendations_thread, daemon=True).start()

    def _load_recommendations_thread(self):
        try:
            result = self.recommendation_service.get_weather_recommendations(self.menu_items)
            print("AI Response received:", bool(result), "success:", result.get('success', False))
        except Exception as e:
            print("Exception in recommendation thread:", str(e))
            result = {'success': False, 'error': str(e)}
        Clock.schedule_once(lambda dt: self._update_ui_with_recommendations(result), 0)

    def _update_ui_with_recommendations(self, result):
        self.is_loading = False
        self.refresh_btn.disabled = False

        if self.spinner in self.layout.children:
            self.layout.remove_widget(self.spinner)

        weather_data = result.get('weather_data', {})
        self.weather_info.text = (
            f"[b]Current Weather:[/b] {weather_data.get('weather_description', 'Unknown')}\n"
            f"[b]Temperature:[/b] {weather_data.get('temperature', 0)}°C, "
            f"[b]Humidity:[/b] {weather_data.get('humidity', 0)}%"
        )

        if result.get('success', False):
            recommendations_text = result.get('recommendations', '')
            print("Adding recommendation text length:", len(recommendations_text))
            self._add_recommendation_sections(recommendations_text)
        else:
            error_msg = result.get('error', 'Unknown error')
            print("Error displaying recommendations:", error_msg)
            error_label = Label(
                text=f"Error: {error_msg}",
                size_hint_y=None,
                height=dp(100),
                markup=True,
                color=(1, 0, 0, 1)
            )
            self.recommendations_container.add_widget(error_label)

    def _add_recommendation_sections(self, text):
        # Use the split_recommendation_text function to parse the recommendations
        recommendations, summary = self.split_recommendation_text(text)

        if not recommendations:
            label = Label(
                text="No recommendations available",
                size_hint_y=None,
                height=dp(100)
            )
            self.recommendations_container.add_widget(label)
            return

        # Add each food recommendation as a separate container
        for i, recommendation in enumerate(recommendations):
            self._add_food_container(recommendation, i+1)

        # Add summary if available
        if summary:
            self._add_summary_container(summary)
    def remove_space_before_parenthesis(self, text):
        """Removes spaces immediately before an opening parenthesis."""
        return re.sub(r'\s+\(', '(', text)
    def _add_food_container(self, text, index):
        # Create container for a single food recommendation
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=dp(10),
            spacing=dp(5)
        )
        container.bind(minimum_height=container.setter('height'))

        # Add background
        with container.canvas.before:
            Color(*COLORS['item_bg'])
            container.bg_rect = Rectangle(size=container.size, pos=container.pos)
        container.bind(size=self._update_bg_rect, pos=self._update_bg_rect)

        # Extract title (first line) and description
        lines = text.split('\n', 1)
        title = lines[0].strip("**")
        description = lines[1] if len(lines) > 1 else ""

        # Create title label with bold font
        title_label = Label(
            text=f"{index}. {title}",
            size_hint_y=None,
            height=dp(30),
            font_size=dp(16),
            bold=True,
            halign='left',
            valign='middle',
            text_size=(None, None),
            color=COLORS['text']
        )
        title_label.bind(
            width=lambda *x: setattr(title_label, 'text_size', (title_label.width, None)),
            texture_size=lambda *x: setattr(title_label, 'height', title_label.texture_size[1])
        )
        container.add_widget(title_label)

        # Create description label
        if description:
            desc_label = Label(
                text=description,
                size_hint_y=None,
                halign='left',
                valign='top',
                text_size=(None, None),
                color=COLORS['text']
            )
            desc_label.bind(
                width=lambda *x: setattr(desc_label, 'text_size', (desc_label.width - dp(10), None)),
                texture_size=lambda *x: setattr(desc_label, 'height', desc_label.texture_size[1] + dp(5))
            )
            container.add_widget(desc_label)

        # Add to cart button if callback provided
        if self.add_to_cart_callback:
            button_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(40),
                padding=dp(5)
            )
            add_btn = Button(
                text="Add to Cart",
                size_hint_x=0.4,
                background_color=(0.3, 0.7, 0.3, 1),
                color=(1, 1, 1, 1),
            )

            # Extract product name from title
            product_match = re.match(r'(.+?)\s*-\s*(.+)', title)
            if product_match:
                product_name = product_match.group(1).strip().lower()
                quantity = product_match.group(2).strip()[0]
                product_name = self.remove_space_before_parenthesis(product_name)
                print(product_name, quantity, sep=" ")
                # Bind the add_to_cart_callback with the product name
                add_btn.bind(on_press=lambda btn, name=product_name, quantity=quantity: self.add_to_cart_callback(name, quantity))
                button_layout.add_widget(add_btn)
                container.add_widget(button_layout)

        self.recommendations_container.add_widget(container)

    def _add_summary_container(self, text):
        # Create container for summary
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=dp(10),
            spacing=dp(5)
        )
        container.bind(minimum_height=container.setter('height'))

        # Add background with different color
        with container.canvas.before:
            Color(*COLORS['summary_bg'])
            container.bg_rect = Rectangle(size=container.size, pos=container.pos)
        container.bind(size=self._update_bg_rect, pos=self._update_bg_rect)

        # Create summary label
        summary_label = Label(
            text=text,
            size_hint_y=None,
            halign='left',
            valign='top',
            text_size=(None, None),
            color=COLORS['text']
        )
        summary_label.bind(
            width=lambda *x: setattr(summary_label, 'text_size', (summary_label.width - dp(10), None)),
            texture_size=lambda *x: setattr(summary_label, 'height', summary_label.texture_size[1] + dp(5))
        )
        container.add_widget(summary_label)

        self.recommendations_container.add_widget(container)

    def _update_bg_rect(self, instance, value):
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size

    def on_dismiss(self):
        # Clean up scheduled events
        for event in self.scheduled_events:
            Clock.unschedule(event)
        self.scheduled_events.clear()

    def split_recommendation_text(self, text : str):
        text = text.replace("*", "")
        lines = [line.strip() for line in text.split('\n')]
        recommendations = []
        summary = ""
        i = 0
        n = len(lines)

        # Duyệt qua từng dòng để phân tích
        while i < n:
            if not lines[i]:
                i += 1
                continue

            # Kiểm tra xem dòng có phải là tiêu đề món ăn không (theo mẫu "[Tên] - [Số lượng]")
            product_match = re.match(r'(.+?)\s*-\s*(.+)', lines[i])
            if product_match:
                item_lines = [lines[i]]
                i += 1
                # Thu thập tất cả các dòng tiếp theo thuộc phần giải thích
                while i < n and not re.match(r'.+?\s*-\s*.+', lines[i]) and lines[i] != "":
                    item_lines.append(lines[i])
                    i += 1
                # Ghép lại thành một chuỗi đầy đủ
                recommendations.append('\n'.join(item_lines))
            elif lines[i].lower().startswith("tóm tắt:") or lines[i].lower() == "summary":
                # Bắt đầu phần tóm tắt
                summary_lines = [lines[i]]
                i += 1
                while i < n and not re.match(r'.+?\s*-\s*.+', lines[i]):
                    if lines[i]:
                        summary_lines.append(lines[i])
                    i += 1
                summary = '\n'.join(summary_lines)
            else:
                i += 1

        return recommendations, summary
