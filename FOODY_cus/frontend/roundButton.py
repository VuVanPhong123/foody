from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.animation import Animation

class RoundedButton(Button):
    def __init__(self, color=(0.2, 0.6, 1, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0) 
        self.color_rgba = list(color)  
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.color_rgba) 
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20, 20, 20, 20])

    def change_color(self, r, g, b, a=1):
        self.color_rgba = [r, g, b, a]
        self.update_canvas()  
    def restore_color(self):
        self.color_rgba = [233/255, 150/255, 14/255, 1]
        self.update_canvas()
    


