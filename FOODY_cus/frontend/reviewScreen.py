import threading, requests
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.spinner import MDSpinner
from kivy.clock import Clock

class ReviewScreen(Screen):
    ENDPOINT = "http://localhost:8008/review"

    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(245/255,177/255,67/255,1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._sync_bg, pos=self._sync_bg)

        self.layout = FloatLayout()
        self.add_widget(self.layout)

        self.stars   = []
        self.rating  = 0
        for i in range(5):
            star = MDFloatingActionButton(icon="star-outline",
                                          md_bg_color=(1,1,1,1),
                                          icon_color=(0,0,0,1),
                                          pos_hint={"center_x":.22+i*.14,
                                                    "center_y":.7})
            star.idx=i+1; star.bind(on_press=self._pick_star)
            self.layout.add_widget(star); self.stars.append(star)

        self.txt = TextInput(hint_text="Viết đánh giá ...",
                             size_hint=(.8,.3),
                             pos_hint={"center_x":.5,"center_y":.45},
                             multiline=True)
        self.layout.add_widget(self.txt)

        self.btn_clear = Button(text="Xóa đánh giá",
                                size_hint=(.4,.1),
                                pos_hint={"x":.05,"y":.18},
                                background_color=(.7,.2,.2,1), color=(1,1,1,1),
                                on_press=self._clear)
        self.layout.add_widget(self.btn_clear)

        self.btn_send = Button(text="Xác nhận",
                               size_hint=(.4,.1),
                               pos_hint={"x":.55,"y":.18},
                               background_color=(.2,.6,.2,1), color=(1,1,1,1),
                               on_press=self._submit_clicked)
        self.layout.add_widget(self.btn_send)

        self.back = MDFloatingActionButton(icon="arrow-left",
                                           md_bg_color=(233/255,150/255,14/255,1),
                                           pos_hint={"center_x":.18,"center_y":.1},
                                           on_release=lambda *_: setattr(self.manager,"current","settings"))
        self.add_widget(self.back)

    def _pick_star(self, w):
        self.rating = w.idx
        for s in self.stars:
            if s.idx<=self.rating:
                s.icon="star"; s.md_bg_color=(233/255,150/255,14/255,1)
            else:
                s.icon="star-outline"; s.md_bg_color=(1,1,1,1)

    def _clear(self,*_):
        self.rating=0; self.txt.text=""
        for s in self.stars: s.icon="star-outline"; s.md_bg_color=(1,1,1,1)

    def _start_spin(self, btn):
        btn.disabled=True
        sp=MDSpinner(size_hint=(None,None),size=(30,30),line_width=2,
                     pos_hint={"center_x":.5,"center_y":.5})
        btn.add_widget(sp); return sp
    def _stop_spin(self, btn, sp):
        if sp.parent: btn.remove_widget(sp)
        btn.disabled=False

    def _submit_clicked(self,*_):
        if self.rating==0 and not self.txt.text.strip():
            self._popup("Đánh giá trống"); return
        sp=self._start_spin(self.btn_send)
        data={"stars":self.rating,"comment":self.txt.text.strip()}
        threading.Thread(target=self._send_worker,args=(data,sp),daemon=True).start()

    def _send_worker(self,data,sp):
        try:
            r=requests.post(self.ENDPOINT,json=data,timeout=5)
            ok=r.status_code==200; msg="Gửi thành công" if ok else r.text
        except Exception as e:
            ok=False; msg=f"Lỗi: {e}"
        Clock.schedule_once(lambda *_: self._after_send(ok,msg,sp))

    def _after_send(self,ok,msg,sp):
        self._stop_spin(self.btn_send,sp)
        self._popup(msg)
        if ok: self._clear()

    def _popup(self,msg):
        Popup(title="Thông báo", content=Label(text=msg),
              size_hint=(None,None), size=(300,150)).open()

    def _sync_bg(self,*_): self.bg.size=self.size; self.bg.pos=self.pos
