import threading, requests, hashlib
from functools import partial
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout  import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput  import TextInput
from kivy.uix.button      import Button
from kivymd.uix.button    import MDFloatingActionButton
from kivymd.uix.spinner   import MDSpinner
from kivy.clock           import Clock
from kivy.graphics        import Color, Rectangle
from frontend.roundButton import RoundedButton


class ChatScreenOwn(Screen):
    ENDPOINT = "http://localhost:8009/chat"
    POLL_SEC = 3

    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(245/255, 177/255, 67/255, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._bg, pos=self._bg)

        root = BoxLayout(orientation="vertical")

        top = BoxLayout(size_hint=(1, .12), padding=10)
        top.add_widget(
            MDFloatingActionButton(icon="arrow-left",
                                   md_bg_color=(233/255, 150/255, 14/255, 1),
                                   icon_color=(0, 0, 0, 1),
                                   on_press=lambda *_:
                                   setattr(self.manager, "current", "settings_owner"))
        )

        self.scroll = ScrollView(size_hint=(1, .78))
        self.box = BoxLayout(orientation="vertical", size_hint_y=None,
                             spacing=10, padding=10)
        self.box.bind(minimum_height=self.box.setter("height"))
        self.scroll.add_widget(self.box)

        bottom = BoxLayout(size_hint=(1, .10), spacing=10, padding=10)
        self.txt = TextInput(multiline=False, hint_text="Nhập tin nhắn",
                             size_hint=(.8, 1))
        self.btn = Button(text="Gửi", size_hint=(.2, 1),
                          background_color=(233/255, 150/255, 14/255, 1),
                          on_press=self._send)
        bottom.add_widget(self.txt)
        bottom.add_widget(self.btn)

        root.add_widget(top)
        root.add_widget(self.scroll)
        root.add_widget(bottom)
        self.add_widget(root)

        self.last_id = 0
        self.seen_ids = set()
        self.pending = {}
        self.polling = False
        self.poll_ev = None

        self.center_spin = MDSpinner(size_hint=(None, None), size=(46, 46),
                                     line_width=3,
                                     pos_hint={"center_x": .5, "center_y": .5})
        self.center_spin.active = True
        self.add_widget(self.center_spin)

    def _bg(self, *_):
        self.bg.size, self.bg.pos = self.size, self.pos

    def _hash(self, s, m):
        return hashlib.md5(f"{s}:{m}".encode()).hexdigest()

    def _bubble(self, sender, msg, mine):
        col = (233/255, 150/255, 14/255, 1) if mine else (0.9, 0.4, 0.1, 1)
        b = RoundedButton(text=f"{sender}:\n{msg}", size_hint=(None, None),
                          width=320, halign="left", valign="middle",
                          text_size=(280, None))
        b.change_color(*col)
        b.color = (0, 0, 0, 1)
        b.bind(texture_size=lambda w, s: setattr(w, "height", s[1] + 20))
        self.box.add_widget(b)
        return b

    def _scroll_bottom(self):
        Clock.schedule_once(lambda *_: setattr(self.scroll, "scroll_y", 0), 0)

    def on_pre_enter(self, *_):
        self._poll()
        self.poll_ev = Clock.schedule_interval(lambda dt: self._poll(), self.POLL_SEC)

    def on_leave(self, *_):
        if self.poll_ev:
            self.poll_ev.cancel()
            self.poll_ev = None

    def _poll(self):
        if self.polling:
            return
        self.polling = True
        threading.Thread(target=self._poll_worker, daemon=True).start()

    def _poll_worker(self):
        try:
            rows = requests.get(f"{self.ENDPOINT}?after_id={self.last_id}", timeout=3).json()
        except Exception:
            rows = []
        Clock.schedule_once(partial(self._after_poll, rows))

    def _after_poll(self, rows, *_):
        self.polling = False
        if self.center_spin.parent and rows:
            self.remove_widget(self.center_spin)

        for r in rows:
            rid = r["id"]
            self.last_id = max(self.last_id, rid)
            if rid in self.seen_ids:
                continue

            if r.get("owner"):
                h = self._hash("Me", r["owner"])
                if h in self.pending:
                    self.pending.pop(h).text = f"Me:\n{r['owner']}"
                else:
                    self._bubble("Me", r["owner"], mine=True)

            if r.get("customer"):
                self._bubble("Customer", r["customer"], mine=False)

            self.seen_ids.add(rid)

        if rows:
            self._scroll_bottom()

    def _send(self, *_):
        text = self.txt.text.strip()
        if not text:
            return
        self.txt.text = ""
        h = self._hash("Me", text)
        if h in self.pending:
            return
        self.pending[h] = self._bubble("Me", text, mine=True)
        self._scroll_bottom()
        threading.Thread(target=self._send_worker, args=(text, h), daemon=True).start()

    def _send_worker(self, text, h):
        try:
            ok = requests.post(self.ENDPOINT,
                               json={"sender": "owner", "message": text},
                               timeout=3).status_code == 201
        except Exception:
            ok = False

        if not ok:
            Clock.schedule_once(
                lambda *_: setattr(self.pending.pop(h, None), 'text', "(!)\n[Không gửi được]")
            )
