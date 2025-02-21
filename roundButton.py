from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.animation import Animation

class RoundedButton(Button):
    def __init__(self, color=(0.2, 0.6, 1, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)  # Hide default background
        self.color_rgba = list(color)  # Store initial color as a list
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.color_rgba)  # Use stored color
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20, 20, 20, 20])

    def change_color(self, r, g, b, a=1):
        """Change the button color dynamically."""
        self.color_rgba = [r, g, b, a]
        self.update_canvas()  # Redraw with new color
    def shrink(self, a):  
        if a == 1:
            new_width = self.width * 0.80
            new_height = self.height * 0.80
            new_font_size = self.font_size * 0.80  # Shrink text
        elif a == 2:
            new_width = self.width * 0.64
            new_height = self.height * 0.64
            new_font_size = self.font_size * 0.64  # Shrink text more
        else:
            return  

        new_x = self.x + (self.width - new_width) / 2
        new_y = self.y + (self.height - new_height) / 2

        anim = Animation(size=(new_width, new_height), 
                         pos=(new_x, new_y), 
                         font_size=new_font_size,  # Animate text size
                         duration=0.1)
        anim.start(self)

    def big(self, a):
        if a == 1:
            new_width = self.width * 1.25
            new_height = self.height * 1.25
            new_font_size = self.font_size * 1.25  # Enlarge text
        elif a == 2:
            new_width = self.width * 1.5625
            new_height = self.height * 1.5625
            new_font_size = self.font_size * 1.5625  # Enlarge text more
        else:
            return  

        new_x = self.x - (new_width - self.width) / 2
        new_y = self.y - (new_height - self.height) / 2

        anim = Animation(size=(new_width, new_height), 
                         pos=(new_x, new_y), 
                         font_size=new_font_size,  # Animate text size
                         duration=0.1)
        anim.start(self)




