import requests, threading, pandas as pd
from kivy.uix.label      import Label
from kivy.uix.textinput  import TextInput
from kivy.uix.button     import Button
from kivy.uix.boxlayout  import BoxLayout
from kivy.uix.floatlayout  import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.graphics       import Color, Rectangle
from kivy.clock          import Clock
from kivymd.uix.spinner  import MDSpinner
from frontend.roundButton import RoundedButton


class Ingredients(Screen):
    ENDPOINT = "http://localhost:8000/ingredients"

    def _show_spinner(self):
        if getattr(self, "_overlay", None):
            return
        overlay = FloatLayout(size=self.size, pos=self.pos)
        with overlay.canvas.before:
            Color(0, 0, 0, .25)
            overlay._rect = Rectangle(size=self.size, pos=self.pos)

        spinner = MDSpinner(size_hint=(None, None), size=(60, 60),
                            line_width=3, pos_hint={"center_x": .5,
                                                    "center_y": .5})
        overlay.add_widget(spinner)
        self.add_widget(overlay)
        self._overlay = overlay

    def _hide_spinner(self):
        if getattr(self, "_overlay", None):
            self.remove_widget(self._overlay)
            self._overlay = None

    def __init__(self, **kw):
        super().__init__(**kw)

        with self.canvas.before:
            Color(245/255, 177/255, 67/255, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._sync_bg, pos=self._sync_bg)

        self.ingredients_data = {}

        root = BoxLayout(orientation="vertical", padding=10, spacing=10)
        self.notice = Label(size_hint_y=None, height=28, color=(1, 0, 0, 1))
        root.add_widget(self.notice)

        self.scroll = ScrollView(size_hint=(1, .6))
        self.list_box = BoxLayout(orientation="vertical", size_hint_y=None,
                                  spacing=10, padding=10)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        self.scroll.add_widget(self.list_box)
        root.add_widget(self.scroll)

        inp_line = BoxLayout(size_hint_y=None, height=50, spacing=5)
        self.in_name   = TextInput(hint_text="Tên NL", size_hint_x=.4)
        self.in_qty    = TextInput(hint_text="Số lượng", input_filter="float", size_hint_x=.2)
        self.in_unit   = TextInput(hint_text="Đơn vị",   size_hint_x=.2)
        self.in_date   = TextInput(hint_text="Ngày mua YYYY-MM-DD",  size_hint_x=.4)
        self.in_expiry = TextInput(hint_text="Hạn dùng YYYY-MM-DD",  size_hint_x=.4)
        for w in (self.in_name, self.in_qty, self.in_unit, self.in_date, self.in_expiry):
            inp_line.add_widget(w)
        root.add_widget(inp_line)

        add_line = BoxLayout(size_hint_y=None, height=50)
        self.btn_add = RoundedButton(text="Thêm nguyên liệu",
                                     on_press=self._add_clicked)
        self._style_btn(self.btn_add)
        add_line.add_widget(self.btn_add)
        root.add_widget(add_line)

        self.add_widget(root)
        self._load_async()

    def _style_btn(self, b):
        b.change_color(233/255, 150/255, 14/255, 1)
        b.color = (0, 0, 0, 1)

    def _sync_bg(self, *_):
        self.bg.size, self.bg.pos = self.size, self.pos
        if getattr(self, "_overlay", None):
            self._overlay[1].size, self._overlay[1].pos = self.size, self.pos

    def _notify(self, msg):
        self.notice.text = msg
        Clock.schedule_once(lambda *_: setattr(self.notice, "text", ""), 3)

    def _load_async(self):
        self._show_spinner()
        threading.Thread(target=self._fetch_worker, daemon=True).start()

    def _fetch_worker(self):
        try:
            data = requests.get(self.ENDPOINT, timeout=5).json()
            err = None
        except Exception as e:
            data, err = [], str(e)
        Clock.schedule_once(lambda *_: self._after_fetch(data, err))

    def _after_fetch(self, data, err):
        self._hide_spinner()
        self.list_box.clear_widgets()
        if err:
            self._notify(f"Lỗi tải: {err}"); return
        self.ingredients_data = {d["ingredient"]: d for d in data}
        for item in data:
            self._add_row(item)

    def _add_row(self, item):
        ing = item["ingredient"]
        txt = f"{ing} {round(item['quantity'],2)} {item['unit']} " \
              f"(mua: {item['purchase_date']} | hạn: {item['expiry_date']})"
        box = BoxLayout(orientation="vertical", size_hint_y=None, height=85, spacing=5)
        box.add_widget(Label(text=txt, size_hint_y=None, height=40, color=(0, 0, 0, 1)))

        line = BoxLayout(size_hint_y=None, height=40, spacing=5)
        inp  = TextInput(hint_text="Nhập số", input_filter="float", size_hint_x=.35)
        btn_use = RoundedButton(text="Sử dụng", size_hint_x=.325,
                                on_press=lambda *_: self._use_clicked(ing, inp))
        btn_del = RoundedButton(text="Xóa", size_hint_x=.325,
                                on_press=lambda *_: self._del_clicked(ing))
        for b in (btn_use, btn_del): self._style_btn(b)
        line.add_widget(inp); line.add_widget(btn_use); line.add_widget(btn_del)
        box.add_widget(line)
        self.list_box.add_widget(box)

    def _use_clicked(self, ing, inp):
        amt = inp.text.strip()
        if not self._valid_amount(amt, ing):
            self._notify("Số lượng không hợp lệ"); return
        self._show_spinner()
        threading.Thread(target=self._use_worker,
                         args=(ing, float(amt)), daemon=True).start()

    def _use_worker(self, ing, amt):
        try:
            r = requests.put(f"{self.ENDPOINT}/{ing}",
                             params={"used_amount": amt}, timeout=5)
            ok, msg = (r.status_code == 200), r.text
        except Exception as e:
            ok, msg = False, str(e)
        Clock.schedule_once(lambda *_: self._after_action(ok, msg))

    def _del_clicked(self, ing):
        self._show_spinner()
        threading.Thread(target=self._del_worker, args=(ing,), daemon=True).start()

    def _del_worker(self, ing):
        try:
            r = requests.delete(f"{self.ENDPOINT}/{ing}", timeout=5)
            ok, msg = (r.status_code == 200), r.text
        except Exception as e:
            ok, msg = False, str(e)
        Clock.schedule_once(lambda *_: self._after_action(ok, msg))

    def _add_clicked(self, *_):
        vals = (self.in_name.text.strip(), self.in_qty.text.strip(),
                self.in_unit.text.strip(), self.in_date.text.strip(),
                self.in_expiry.text.strip())
        if not all(vals):
            self._notify("Điền đủ thông tin"); return
        body = {"name": vals[0], "quantity": float(vals[1]), "unit": vals[2],
                "purchase_date": vals[3], "expiry_date": vals[4]}
        self._show_spinner()
        threading.Thread(target=self._add_worker, args=(body,), daemon=True).start()

    def _add_worker(self, body):
        try:
            r = requests.post(self.ENDPOINT, json=body, timeout=5)
            ok, msg = (r.status_code == 200), r.text
        except Exception as e:
            ok, msg = False, str(e)
        Clock.schedule_once(lambda *_: self._after_action(ok, msg))

    def _after_action(self, ok, msg):
        self._hide_spinner()
        self._notify("Thành công" if ok else f"Lỗi: {msg}")
        if ok:
            self._load_async()

    def _valid_amount(self, s, ing):
        try:
            v = float(s)
            return 0 < v <= self.ingredients_data.get(ing, {}).get("quantity", 0)
        except ValueError:
            return False
