from frontend.roundButton import RoundedButton
import os, ast, requests, threading
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen, ScreenManager, FallOutTransition
from kivy.graphics import Color, Rectangle
from kivymd.uix.button import MDIconButton, MDFloatingActionButton
from kivymd.uix.spinner import MDSpinner
from frontend.settingsScreen import SettingsScreen
from frontend.geminiChatScreen import GeminiChatScreen

class AsyncMixin:
    def _show_spinner(self):
        if getattr(self, "_sp", None) is None:
            self._sp = MDSpinner(size_hint=(None, None), size=(46, 46), line_width=3, color=(1, 1, 1, 1), pos_hint={"center_x": .5, "center_y": .5})
            self.add_widget(self._sp)
    def _hide_spinner(self):
        if getattr(self, "_sp", None):
            self.remove_widget(self._sp)
            self._sp = None
    def _run_async(self, fn, cb, *a):
        self._show_spinner()
        def w():
            try:
                r = fn(*a); e = None
            except Exception as ex:
                r, e = None, ex
            Clock.schedule_once(lambda dt: cb(r, e))
        threading.Thread(target=w, daemon=True).start()

class MenuScreen(Screen, AsyncMixin):
    def __init__(self, **k):
        super().__init__(**k)
        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._rc, pos=self._rc)
        self.layout = FloatLayout()
        self.scroll = ScrollView(size_hint=(.98, .8), pos_hint={"center_x": .5, "center_y": .55})
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container)
        self.layout.add_widget(self.scroll)
        self.confirm = RoundedButton(text="Thêm vào giỏ hàng", size_hint=(None, None), size=(250, 50), pos_hint={"center_x": .5, "y": .02}, font_size=18)
        self.confirm.change_color(.9, .4, .1, 1); self.confirm.color = (0, 0, 0, 1)
        self.confirm.bind(on_press=self._save_cart)
        self.gem = MDFloatingActionButton(icon="robot", md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1), pos_hint={"x": .02, "y": .02})
        self.gem.bind(on_press=lambda *_: setattr(self.manager, 'current', 'gemini'))
        self.layout.add_widget(self.gem)
        self.layout.add_widget(self.confirm)
        self.add_widget(self.layout)
        self.menu_items = []
        self.selected = {}
        self.inputs = {}
        self._run_async(lambda: requests.get("http://localhost:8003/menu", timeout=5).json(), self._after_menu)
    def _rc(self, *a):
        self.rect.size, self.rect.pos = self.size, self.pos
    def _after_menu(self, data, err):
        self._hide_spinner()
        if err:
            self.container.add_widget(Label(text=f"Lỗi: {err}", color=(1, 0, 0, 1)))
            return
        self.menu_items = data or []
        self.selected = {i['name']: 0 for i in self.menu_items}
        self._build()
    def _build(self):
        self.container.clear_widgets()
        for it in self.menu_items:
            n, p, img = it['name'], it['price'], it['image']
            if not os.path.exists(img):
                img = "images/default.png"
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=100)
            row.add_widget(Image(source=img, size_hint=(.2, 1)))
            info = BoxLayout(orientation='vertical', size_hint=(.4, 1), padding=5, spacing=2)
            name_l = Label(text=n, color=(0, 0, 0, 1), halign="left", valign="middle")
            price_l = Label(text=f"Giá: {p}đ", color=(0, 0, 0, 1), halign="left", valign="middle")
            info.add_widget(name_l); info.add_widget(price_l); row.add_widget(info)
            ctl = BoxLayout(size_hint=(.4, 1), spacing=5)
            minus = Button(text="-", size_hint=(.2, 1), background_color=(.8, .2, .2, 1), color=(1, 1, 1, 1))
            plus = Button(text="+", size_hint=(.2, 1), background_color=(.8, .2, .2, 1), color=(1, 1, 1, 1))
            qty = TextInput(text="0", size_hint=(.3, 1), multiline=False, halign="center")
            qty.bind(text=self._upd(n))
            self.inputs[n] = qty
            minus.bind(on_press=lambda *_: self._delta(n, -1))
            plus.bind(on_press=lambda *_: self._delta(n, 1))
            ctl.add_widget(minus); ctl.add_widget(qty); ctl.add_widget(plus)
            row.add_widget(ctl)
            self.container.add_widget(row)
    def _upd(self, k):
        def f(instance, val):
            try: q = max(0, int(val))
            except ValueError: q = 0
            self.selected[k] = q
        return f
    def _delta(self, k, d):
        self.selected[k] = max(0, self.selected[k] + d)
        self.inputs[k].text = str(self.selected[k])
    def _save_cart(self, *_):
        if not any(self.selected.values()):
            self._pop("Bạn chưa chọn gì!")
            return
        body = {"quantities": self.selected, "menu_items": self.menu_items}
        self._run_async(lambda: requests.post("http://localhost:8004/cart", json=body, timeout=5).status_code, self._after_cart)
    def _after_cart(self, code, err):
        self._hide_spinner()
        if err or code != 200:
            self._pop("Lỗi khi thêm vào giỏ hàng")
        else:
            self._pop("Đã thêm vào giỏ hàng!")
            for k in self.selected:
                self.selected[k] = 0
                self.inputs[k].text = "0"
    def _pop(self, m):
        Popup(title="Thông báo", content=Label(text=m), size_hint=(None, None), size=(320, 180)).open()

class CartScreen(Screen, AsyncMixin):
    def __init__(self, **k):
        super().__init__(**k)
        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._r, pos=self._r)
        self.layout = FloatLayout()
        self.scroll = ScrollView(size_hint=(.98, .82), pos_hint={"center_x": .5, "center_y": .55})
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container)
        self.layout.add_widget(self.scroll)
        buy = RoundedButton(text="Mua tất cả", size_hint=(None, None), size=(250, 50), pos_hint={"center_x": .5, "y": .02}, font_size=18)
        buy.change_color(.9, .4, .1, 1)
        buy.bind(on_press=lambda *_: self._pop("Chức năng đang phát triển"))
        self.layout.add_widget(buy)
        self.add_widget(self.layout)
    def _r(self, *a): self.rect.size, self.rect.pos = self.size, self.pos
    def on_pre_enter(self, *_): self._load()
    def _load(self):
        self._run_async(lambda: requests.get("http://localhost:8004/cart", timeout=5).json(), self._after)
    def _after(self, data, err):
        self._hide_spinner()
        self.container.clear_widgets()
        if err:
            self.container.add_widget(Label(text=f"Lỗi: {err}", color=(1, 0, 0, 1))); return
        if not data:
            self.container.add_widget(Label(text="Bạn không có gì trong giỏ hàng", font_size=18, color=(0, 0, 0, 1))); return
        for row in data:
            names = row["item_names"]; qtys = row["quantities"]
            if isinstance(names, str): names = ast.literal_eval(names)
            if isinstance(qtys, str): qtys = ast.literal_eval(qtys)
            info = "\n".join(f"{i} x{int(q)}" for i, q in zip(names, qtys))
            total = row["total_price"]
            blk = BoxLayout(orientation='vertical', size_hint_y=None, padding=5, spacing=5)
            blk.height = 110 + info.count('\n') * 18
            top = BoxLayout(size_hint_y=.6, spacing=10)
            o = RoundedButton(text=info, size_hint=(.7, 1), halign="left", valign="middle", text_size=(None, None))
            o.change_color(233 / 255, 150 / 255, 14 / 255, 1); o.color = (0, 0, 0, 1); o.bind(texture_size=o.setter("size"))
            p = RoundedButton(text=f"{total}đ", size_hint=(.3, 1)); p.change_color(233 / 255, 150 / 255, 14 / 255, 1); p.color=(0,0,0,1)
            mua = Button(text="Mua", size_hint=(1, None), height=50, background_color=(233 / 255, 150 / 255, 14 / 255, 1), color=(0,0,0,1))
            mua.bind(on_press=lambda *_: self._pop("Chức năng đang phát triển"))
            top.add_widget(o); top.add_widget(p); blk.add_widget(top); blk.add_widget(mua); self.container.add_widget(blk)
    def _pop(self, m): Popup(title="Thông báo", content=Label(text=m), size_hint=(None,None), size=(320,180)).open()
class OrderScreen(Screen, AsyncMixin):
    def __init__(self, **k):
        super().__init__(**k)
        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._r, pos=self._r)
        self.layout = FloatLayout()
        self.scroll = ScrollView(size_hint=(.98, .92), pos_hint={"center_x": .5, "center_y": .5})
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container); self.layout.add_widget(self.scroll); self.add_widget(self.layout)
    def _r(self,*a): self.rect.size,self.rect.pos=self.size,self.pos
    def on_pre_enter(self,*_): self._load(); self.ev=Clock.schedule_interval(lambda dt:self._load(),5)
    def on_leave(self,*_): Clock.unschedule(self.ev)
    def _load(self): self._run_async(lambda: requests.get("http://localhost:8005/orderinfo",timeout=5).json(), self._after)
    def _after(self,data,err):
        self._hide_spinner(); self.container.clear_widgets()
        if err: self.container.add_widget(Label(text=f"Lỗi: {err}",color=(1,0,0,1))); return
        if not data: self.container.add_widget(Label(text="Bạn không có đơn hàng nào",font_size=18,color=(0,0,0,1))); return
        for row in data:
            info = " "+str(row.get("order","")).replace(",","\n").strip()
            price = str(row.get("price",""))
            blk = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5, padding=5)
            top = BoxLayout(size_hint_y=None, spacing=10)
            o = RoundedButton(text=info, size_hint=(.7,None), halign="left", valign="middle", text_size=(None,None))
            o.change_color(233/255,150/255,14/255,1); o.color=(0,0,0,1); o.texture_update(); h=o.texture_size[1]+20; o.height=h
            p = RoundedButton(text=f"{price}đ", size_hint=(.3,None), height=h); p.change_color(233/255,150/255,14/255,1); p.color=(0,0,0,1)
            top.height=h; top.add_widget(o); top.add_widget(p); blk.add_widget(top)
            self.container.add_widget(blk)

class HistoryScreen(Screen, AsyncMixin):
    def __init__(self, **k):
        super().__init__(**k)
        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._r, pos=self._r)
        self.layout = BoxLayout(orientation='vertical', padding=5, spacing=5)
        self.scroll = ScrollView(size_hint=(1,1))
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container); self.layout.add_widget(self.scroll); self.add_widget(self.layout)
    def _r(self,*a): self.rect.size,self.rect.pos=self.size,self.pos
    def on_pre_enter(self,*_): self._load(); self.ev=Clock.schedule_interval(lambda dt:self._load(),5)
    def on_leave(self,*_): Clock.unschedule(self.ev)
    def _load(self): self._run_async(lambda: requests.get("http://localhost:8007/history",timeout=5).json(), self._after)
    def _after(self,data,err):
        self._hide_spinner(); self.container.clear_widgets()
        if err: self.container.add_widget(Label(text=f"Lỗi: {err}",color=(1,0,0,1))); return
        if not data: self.container.add_widget(Label(text="Không có lịch sử đơn hàng",font_size=18,color=(0,0,0,1))); return
        for e in data:
            food=" "+e.get("order","").replace(", ","\n").strip()
            price=f"{e.get('price',0)}đ"
            dt=f"{e.get('date','--')}\n{e.get('time','--')}"
            st=e.get("status","")
            row=BoxLayout(orientation='vertical',size_hint_y=None,spacing=10,padding=10)
            top=BoxLayout(size_hint_y=None,spacing=10)
            t=RoundedButton(text=dt,size_hint=(.2,None)); t.change_color(233/255,150/255,14/255,1); t.color=(0,0,0,1)
            o=RoundedButton(text=food,size_hint=(.6,None),halign="left",valign="middle",text_size=(None,None)); o.change_color(233/255,150/255,14/255,1); o.color=(0,0,0,1)
            p=RoundedButton(text=price,size_hint=(.2,None)); p.change_color(233/255,150/255,14/255,1); p.color=(0,0,0,1)
            o.texture_update(); h=o.texture_size[1]+20; o.height=h; t.height=h; p.height=h; top.height=h
            top.add_widget(t); top.add_widget(o); top.add_widget(p)
            status=Button(text=st,size_hint_y=None,height=40,background_color=(.1,.6,.1,1) if st=="Đã hoàn thành" else (.8,.1,.1,1),color=(1,1,1,1))
            row.add_widget(top); row.add_widget(status); row.height=h+60; self.container.add_widget(row)

class MainScreenCus(Screen):
    def __init__(self, **k):
        super().__init__(**k)
        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._r, pos=self._r)
        root = BoxLayout(orientation='vertical')
        top = BoxLayout(size_hint_y=None, height='50dp', padding=('10dp','5dp'), spacing='10dp')
        self.title = Label(text='FOODY', color=(0,0,0,1), halign="left", valign="middle", size_hint=(.4,1))
        self.title.bind(size=self.title.setter('text_size'))
        cog = MDIconButton(icon='cog', md_bg_color=(233/255,150/255,14/255,1), icon_size='20sp')
        cog.bind(on_press=lambda *_: self.manager.current.__setattr__('current','settings'))
        top.add_widget(self.title); top.add_widget(cog); root.add_widget(top)
        tab = BoxLayout(size_hint_y=None, height='40dp')
        self.btns=[]; self.act=None
        def add_tab(txt,scr):
            b=RoundedButton(text=txt,size_hint=(.25,1)); b.change_color(233/255,150/255,14/255,1); b.color=(0,0,0,1)
            b.bind(on_press=lambda *_: self._sel(b,scr)); self.btns.append(b); tab.add_widget(b)
        add_tab("Menu","menu"); add_tab("Giỏ hàng","cart"); add_tab("Đơn hàng","order"); add_tab("Lịch sử","history")
        root.add_widget(tab)
        self.sm=ScreenManager(transition=FallOutTransition())
        self.sm.add_widget(MenuScreen(name="menu")); self.sm.add_widget(CartScreen(name="cart"))
        self.sm.add_widget(OrderScreen(name="order")); self.sm.add_widget(HistoryScreen(name="history"))
        self.sm.add_widget(SettingsScreen(name="settings")); self.sm.add_widget(GeminiChatScreen(name="gemini"))
        root.add_widget(self.sm); self.add_widget(root); self._sel(self.btns[0],"menu")
    def _r(self,*a): self.rect.size,self.rect.pos=self.size,self.pos
    def _sel(self,btn,scr):
        if self.act and self.act!=btn:
            self.act.change_color(233/255,150/255,14/255,1); self.act.color=(0,0,0,1)
        btn.change_color(200/255,100/255,14/255,1); btn.color=(0,0,0,1); self.act=btn; self.sm.current=scr
