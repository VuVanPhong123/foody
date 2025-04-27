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
from kivy.app import App
from functools import partial

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

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._sync_bg, pos=self._sync_bg)

        self.layout = FloatLayout()
        self.add_widget(self.layout)

        self.scroll = ScrollView(size_hint=(.98, .8),
                                 pos_hint={'center_x': .5, 'center_y': .55})
        self.container = BoxLayout(orientation='vertical',
                                   size_hint_y=None,
                                   spacing=10, padding=10)
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container)
        self.layout.add_widget(self.scroll)

        self.confirm_btn = RoundedButton(text="Thêm vào giỏ hàng",
                                         size_hint=(None, None),
                                         size=(250, 50),
                                         pos_hint={'center_x': .5, 'y': .02},
                                         font_size=18)
        self.confirm_btn.change_color(.9, .4, .1, 1)
        self.confirm_btn.color = (0, 0, 0, 1)
        self.confirm_btn.bind(on_press=self.save_to_cart)
        self.layout.add_widget(self.confirm_btn)

        self.gemini_btn = MDFloatingActionButton(icon="robot",
                                                 md_bg_color=(233/255, 150/255, 14/255, 1),
                                                 pos_hint={'x': .02, 'y': .02})
        self.gemini_btn.bind(on_press=self.open_gemini_chat)
        self.layout.add_widget(self.gemini_btn)

        self.spinner = MDSpinner(size_hint=(None, None), size=(46, 46),
                                 line_width=3,
                                 pos_hint={'center_x': .5, 'center_y': .5})

        self.menu_items = []
        self.selected_quantities = {}
        self.qty_inputs = {}

        self._show_spinner()
        threading.Thread(target=self._fetch_menu, daemon=True).start()

    def _fetch_menu(self):
        try:
            r = requests.get("http://localhost:8003/menu", timeout=5)
            data = r.json() if r.status_code == 200 else []
        except Exception:
            data = []
        Clock.schedule_once(lambda *_: self._after_fetch(data))

    def _after_fetch(self, data):
        self._hide_spinner()
        self.menu_items = data
        self.selected_quantities = {it['name']: 0 for it in data}
        self.qty_inputs.clear()
        self._build_menu()

    def _build_menu(self):
        self.container.clear_widgets()
        for item in self.menu_items:
            name, price = item['name'], item['price']
            img = item['image'] if os.path.exists(item['image']) else 'images/default.png'

            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=100)
            row.add_widget(Image(source=img, size_hint=(.2, 1)))

            info = BoxLayout(orientation='vertical', size_hint=(.4, 1),
                             padding=5, spacing=2)
            with info.canvas.before:
                Color(245 / 255, 177 / 255, 67 / 255, 1)
                info.bg = Rectangle(size=info.size, pos=info.pos)
            info.bind(size=self._sync_rect, pos=self._sync_rect)

            lbl_name = Label(text=name, size_hint=(1, .5),
                             halign='left', valign='middle', color=(0,0,0,1))
            lbl_price = Label(text=f"Giá: {price}đ", size_hint=(1, .5),
                              halign='left', valign='middle', color=(0,0,0,1))
            for l in (lbl_name, lbl_price):
                l.bind(size=l.setter('text_size'))
            info.add_widget(lbl_name); info.add_widget(lbl_price)
            row.add_widget(info)

            minus = Button(text='-', size_hint=(.2, 1),
                           background_color=(.78, .2, .2, 1), color=(1,1,1,1))
            qty = TextInput(text='0', size_hint=(.3, 1),
                            multiline=False, halign='center')
            plus = Button(text='+', size_hint=(.2, 1),
                          background_color=(.78, .2, .2, 1), color=(1,1,1,1))

            qty.bind(text=self._make_qty_handler(name))
            minus.bind(on_press=partial(self._change_qty, name, qty, -1))
            plus.bind(on_press=partial(self._change_qty,  name, qty, +1))

            self.qty_inputs[name] = qty

            ctrl = BoxLayout(size_hint=(.4, 1), spacing=5)
            ctrl.add_widget(minus); ctrl.add_widget(qty); ctrl.add_widget(plus)
            row.add_widget(ctrl)

            self.container.add_widget(row)

    def _make_qty_handler(self, name):
        def _h(_, value):
            try:
                self.selected_quantities[name] = max(0, int(value))
            except ValueError:
                self.selected_quantities[name] = 0
        return _h

    def _change_qty(self, name, field, delta, *_):
        new_val = max(0, self.selected_quantities[name] + delta)
        self.selected_quantities[name] = new_val
        field.text = str(new_val)

    def save_to_cart(self, *_):
        if not any(self.selected_quantities.values()):
            self._popup("Bạn chưa chọn gì!")
            return
        body = {"quantities": self.selected_quantities, "menu_items": self.menu_items}
        self._show_spinner()
        threading.Thread(target=self._post_cart, args=(body,), daemon=True).start()

    def _post_cart(self, body):
        try:
            ok = requests.post("http://localhost:8004/cart", json=body, timeout=5).status_code == 200
        except Exception:
            ok = False
        Clock.schedule_once(lambda *_: self._after_post(ok))

    def _after_post(self, ok):
        self._hide_spinner()
        self._popup("Đã thêm vào giỏ hàng!" if ok else "Lỗi khi thêm vào giỏ hàng.")
        if ok:
            for k in self.selected_quantities:
                self.selected_quantities[k] = 0
                self.qty_inputs[k].text = '0'

    def open_gemini_chat(self, *_):
        App.get_running_app().root.current = "gemini"


    def _popup(self, msg):
        Popup(title="Thông báo", content=Label(text=msg),
              size_hint=(None,None), size=(320,180)).open()

    def _show_spinner(self):
        if not self.spinner.parent:
            self.add_widget(self.spinner)

    def _hide_spinner(self):
        if self.spinner.parent:
            self.remove_widget(self.spinner)

    def _sync_rect(self, w, *_):
        w.bg.size = w.size; w.bg.pos = w.pos

    def _sync_bg(self, *_):
        self.bg_rect.size = self.size; self.bg_rect.pos = self.pos

class CartScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._sync_bg, pos=self._sync_bg)

        self.layout = FloatLayout(); self.add_widget(self.layout)
        self.scroll = ScrollView(size_hint=(.98, .82),
                                 pos_hint={'center_x': .5, 'center_y': .55})
        self.rows = BoxLayout(orientation='vertical', size_hint_y=None,
                              spacing=10, padding=10)
        self.rows.bind(minimum_height=self.rows.setter('height'))
        self.scroll.add_widget(self.rows)
        self.layout.add_widget(self.scroll)

        self.buy_all = RoundedButton(text="Mua tất cả",
                                     size_hint=(None, None),
                                     size=(250, 50),
                                     pos_hint={'center_x': .5, 'y': .02},
                                     font_size=18)
        self.buy_all.change_color(.9, .4, .1, 1)
        self.buy_all.bind(on_press=self._buy_all_clicked)
        self.layout.add_widget(self.buy_all)

        self.spinner = MDSpinner(size_hint=(None, None), size=(46, 46),
                                 line_width=3,
                                 pos_hint={'center_x': .5, 'center_y': .5})

        self._current_cart = []   

    def on_pre_enter(self, *_):
        self._reload()

    def _reload(self):
        self._show_spin()
        threading.Thread(target=self._fetch_cart, daemon=True).start()

    def _fetch_cart(self):
        try:
            data = requests.get("http://localhost:8004/cart", timeout=5).json()
        except Exception:
            data = None
        Clock.schedule_once(lambda *_: self._after_fetch(data))

    def _after_fetch(self, cart):
        self._hide_spin()
        self._current_cart = cart or []
        self.rows.clear_widgets()

        if not cart:
            self.rows.add_widget(Label(text="Bạn không có gì trong giỏ hàng",
                                       color=(0, 0, 0, 1), font_size=18,
                                       size_hint=(1, None), height=40))
            return

        for row in cart:
            self.rows.add_widget(self._make_block(row))

    def _make_block(self, row):
        names = row['item_names']; qtys = row['quantities']
        if isinstance(names, str): names = ast.literal_eval(names)
        if isinstance(qtys, str):  qtys  = ast.literal_eval(qtys)
        info = "\n".join(f"{n} x{int(q)}" for n, q in zip(names, qtys))
        total = row['total_price']

        block = BoxLayout(orientation='vertical', size_hint_y=None,
                          padding=5, spacing=5)
        top = BoxLayout(size_hint_y=.6, spacing=10)

        order_btn = RoundedButton(text=info, size_hint=(.7, 1),
                                  halign='left', valign='middle',
                                  text_size=(None, None))
        order_btn.change_color(233/255,150/255,14/255,1); order_btn.color=(0,0,0,1)
        order_btn.bind(texture_size=order_btn.setter('size'))

        price_btn = RoundedButton(text=f"{total}đ", size_hint=(.3, 1))
        price_btn.change_color(233/255,150/255,14/255,1); price_btn.color=(0,0,0,1)

        mua = Button(text="Mua", size_hint=(1, None), height=50,
                     background_color=(233/255,150/255,14/255,1), color=(0,0,0,1))
        mua.bind(on_press=lambda *_: self._popup_buy([row]))

        top.add_widget(order_btn); top.add_widget(price_btn)
        block.add_widget(top); block.add_widget(mua)
        block.height = 110 + info.count('\n') * 18
        return block

    def _buy_all_clicked(self, *_):
        if not self._current_cart:
            self._alert("Không có đơn hàng nào để mua.")
            return
        self._popup_buy(self._current_cart)

    def _popup_buy(self, rows):
        pop = self._order_popup(rows); pop.open()

    def _order_popup(self, rows):
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        name = TextInput(hint_text="Họ tên", size_hint_y=None, height=40); box.add_widget(name)
        phone= TextInput(hint_text="Số điện thoại", size_hint_y=None, height=40); box.add_widget(phone)
        addr = TextInput(hint_text="Địa chỉ", size_hint_y=None, height=40); box.add_widget(addr)
        note = TextInput(hint_text="Ghi chú", size_hint_y=None, height=60); box.add_widget(note)
        ok = Button(text="Xác nhận", size_hint=(1, None), height=50,
                    background_color=(.2,.6,.2,1), color=(1,1,1,1)); box.add_widget(ok)
        pop = Popup(title="Thông tin đơn hàng", content=box,
                    size_hint=(None,None), size=(400,450))
        ok.bind(on_press=lambda *_: self._confirm(pop, name.text, phone.text,
                                                  addr.text, note.text, rows))
        return pop

    def _confirm(self, pop, name, phone, addr, note, rows):
        pop.dismiss()
        if not all([name.strip(), phone.strip(), addr.strip()]):
            self._alert("Vui lòng điền đầy đủ họ tên, số điện thoại và địa chỉ."); return
        self._show_spin()
        threading.Thread(target=self._send_orders,
                         args=(name, phone, addr, note, rows),
                         daemon=True).start()

    def _send_orders(self, name, phone, addr, note, rows):
        ok = True
        try:
            for row in rows:
                items = row['item_names']; qtys = row['quantities']
                if isinstance(items, str): items = ast.literal_eval(items)
                if isinstance(qtys, str):  qtys  = ast.literal_eval(qtys)
                body = {"order": ", ".join(f"{i} x{q}" for i,q in zip(items, qtys)),
                        "price": row['total_price'],
                        "name": name, "address": addr, "note": note, "phone": phone}
                requests.post("http://localhost:8005/orderinfo", json=body, timeout=5)
                requests.delete("http://localhost:8004/cart", json=row, timeout=5)
        except Exception:
            ok = False
        Clock.schedule_once(lambda *_: self._after_send(ok))

    def _after_send(self, ok):
        self._hide_spin()
        self._alert("Đã gửi đơn hàng thành công." if ok else "Có lỗi xảy ra.")
        if ok:
            self._reload()

    def _alert(self, msg):
        Popup(title="Thông báo", content=Label(text=msg),
              size_hint=(None,None), size=(350,200)).open()

    def _show_spin(self):
        if not self.spinner.parent:
            self.add_widget(self.spinner)

    def _hide_spin(self):
        if self.spinner.parent:
            self.remove_widget(self.spinner)

    def _sync_bg(self, *_):
        self.bg.size = self.size; self.bg.pos = self.pos
class OrderScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self._bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._sync_bg, pos=self._sync_bg)
        self._root = FloatLayout()
        self._scroll = ScrollView(size_hint=(.98, .92), pos_hint={'center_x': .5, 'center_y': .5})
        self._rows = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self._rows.bind(minimum_height=self._rows.setter('height'))
        self._scroll.add_widget(self._rows)
        self._root.add_widget(self._scroll)
        self.add_widget(self._root)
        self._spinner = MDSpinner(size_hint=(None, None), size=(46, 46), line_width=3, pos_hint={'center_x': .5, 'center_y': .5})

    def on_pre_enter(self, *_):
        self._reload()
        self._ticker = Clock.schedule_interval(lambda dt: self._reload(), 30)

    def on_leave(self, *_):
        if hasattr(self, '_ticker'):
            self._ticker.cancel()

    def _reload(self):
        self._show_spin()
        threading.Thread(target=self._fetch, daemon=True).start()

    def _fetch(self):
        try:
            data = requests.get("http://localhost:8005/orderinfo", timeout=5).json()
        except Exception:
            data = None
        Clock.schedule_once(lambda *_: self._after_fetch(data))

    def _after_fetch(self, data):
        self._hide_spin()
        self._rows.clear_widgets()
        if not data:
            self._rows.add_widget(Label(text="Bạn không có đơn hàng nào", font_size=18, color=(0, 0, 0, 1), size_hint=(1, None), height=40))
            return
        self._iter = iter(enumerate(data))
        Clock.schedule_interval(self._build_rows, 0)

    def _build_rows(self, *_dt, batch=6):
        for _ in range(batch):
            try:
                idx, row = next(self._iter)
            except StopIteration:
                return False
            self._rows.add_widget(self._make_block(idx, row))
        return True

    def _make_block(self, idx, row):
        txt = (' ' + str(row.get("order", "")).replace(",", "\n").strip())
        price = row.get("price", "")
        block = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5, padding=5)
        top = BoxLayout(size_hint_y=None, spacing=10)
        order_btn = RoundedButton(text=txt, size_hint=(.7, None), halign="left", valign="middle", text_size=(None, None))
        order_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1); order_btn.color = (0, 0, 0, 1)
        order_btn.texture_update(); h = order_btn.texture_size[1] + 20; order_btn.height = h
        price_btn = RoundedButton(text=f"{price}đ", size_hint=(.3, None), height=h)
        price_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1); price_btn.color = (0, 0, 0, 1)
        top.height = h; top.add_widget(order_btn); top.add_widget(price_btn)
        change_btn = Button(text="Thay đổi thông tin", size_hint_y=None, height=40, background_color=(.1, .3, .6, 1), color=(1, 1, 1, 1))
        delete_btn = Button(text="Hủy đơn", size_hint_y=None, height=40, background_color=(.7, .2, .2, 1), color=(1, 1, 1, 1))
        change_btn.bind(on_press=lambda *_: self._edit(idx, row))
        delete_btn.bind(on_press=lambda *_: self._delete(idx))
        block.add_widget(top); block.add_widget(change_btn); block.add_widget(delete_btn)
        block.height = h + 80
        return block

    def _edit(self, idx, row):
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        name = TextInput(text=str(row.get("name", "")), hint_text="Họ tên", size_hint_y=None, height=40); box.add_widget(name)
        phone = TextInput(text=str(row.get("phone", "")), hint_text="SĐT", size_hint_y=None, height=40); box.add_widget(phone)
        addr = TextInput(text=str(row.get("address", "")), hint_text="Địa chỉ", size_hint_y=None, height=40); box.add_widget(addr)
        note = TextInput(text=str(row.get("note", "")), hint_text="Ghi chú", size_hint_y=None, height=60); box.add_widget(note)
        ok = Button(text="Xác nhận", size_hint=(1, None), height=50, background_color=(.2, .6, .2, 1), color=(1, 1, 1, 1)); box.add_widget(ok)
        pop = Popup(title="Chỉnh sửa đơn hàng", content=box, size_hint=(None, None), size=(400, 450))
        ok.bind(on_press=lambda *_: self._update(idx, name.text, phone.text, addr.text, note.text, row["order"], row["price"], pop))
        pop.open()

    def _update(self, idx, n, p, a, note, order, price, pop):
        pop.dismiss()
        body = {"order": order, "price": price, "name": n, "address": a, "note": note, "phone": p}
        threading.Thread(target=lambda: requests.put(f"http://localhost:8005/orderinfo/{idx}", json=body, timeout=5) and Clock.schedule_once(lambda *_: self._reload()), daemon=True).start()

    def _delete(self, idx):
        threading.Thread(target=lambda: requests.delete(f"http://localhost:8005/orderinfo/{idx}", timeout=5) and Clock.schedule_once(lambda *_: self._reload()), daemon=True).start()

    def _alert(self, msg):
        Popup(title="Thông báo", content=Label(text=msg), size_hint=(None, None), size=(350, 200)).open()

    def _show_spin(self):
        if self._spinner.parent is None:
            self.add_widget(self._spinner)

    def _hide_spin(self):
        if self._spinner.parent is not None:
            self.remove_widget(self._spinner)

    def _sync_bg(self, *_):
        self._bg.size = self.size
        self._bg.pos = self.pos


class HistoryScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self._bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._sync_bg, pos=self._sync_bg)
        self._root = FloatLayout()
        self._scroll = ScrollView(size_hint=(1, 1))
        self._rows = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self._rows.bind(minimum_height=self._rows.setter('height'))
        self._scroll.add_widget(self._rows)
        self._root.add_widget(self._scroll)
        self.add_widget(self._root)
        self._spinner = MDSpinner(size_hint=(None, None), size=(46, 46), line_width=3, pos_hint={'center_x': .5, 'center_y': .5})

    def on_pre_enter(self, *_):
        self._reload()
        self._ticker = Clock.schedule_interval(lambda dt: self._reload(), 30)

    def on_leave(self, *_):
        if hasattr(self, '_ticker'):
            self._ticker.cancel()

    def _reload(self):
        self._show_spin()
        threading.Thread(target=self._fetch, daemon=True).start()

    def _fetch(self):
        try:
            data = requests.get("http://localhost:8007/history", timeout=5).json()
        except Exception:
            data = None
        Clock.schedule_once(lambda *_: self._after_fetch(data))

    def _after_fetch(self, data):
        self._hide_spin()
        self._rows.clear_widgets()
        if not data:
            self._rows.add_widget(Label(text="Không có lịch sử đơn hàng", font_size=18, color=(0, 0, 0, 1)))
            return
        self._iter = iter(data)
        Clock.schedule_interval(self._build_rows, 0)

    def _build_rows(self, *_dt, batch=6):
        for _ in range(batch):
            try:
                row = next(self._iter)
            except StopIteration:
                return False
            self._rows.add_widget(self._make_block(row))
        return True

    def _make_block(self, row):
        food = " " + row.get("order", "").replace(", ", "\n").strip()
        price = f"{row.get('price', 0)}đ"
        dtxt = f"{row.get('date', '--')}\n{row.get('time', '--')}"
        stat = row.get("status", "")
        block = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        top = BoxLayout(size_hint_y=None, spacing=10)
        t_btn = RoundedButton(text=dtxt, size_hint=(.2, None), halign="center", valign="middle", text_size=(None, None))
        t_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1); t_btn.color = (0, 0, 0, 1)
        o_btn = RoundedButton(text=food, size_hint=(.6, None), halign="left", valign="middle", text_size=(None, None))
        o_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1); o_btn.color = (0, 0, 0, 1)
        p_btn = RoundedButton(text=price, size_hint=(.2, None))
        p_btn.change_color(233 / 255, 150 / 255, 14 / 255, 1); p_btn.color = (0, 0, 0, 1)
        o_btn.texture_update(); h = o_btn.texture_size[1] + 20
        for b in (t_btn, o_btn, p_btn): b.height = h
        top.height = h; top.add_widget(t_btn); top.add_widget(o_btn); top.add_widget(p_btn)
        s_btn = Button(text=stat, size_hint_y=None, height=40, background_color=(.1, .6, .1, 1) if stat == "Đã hoàn thành" else (.8, .1, .1, 1), color=(1, 1, 1, 1))
        block.add_widget(top); block.add_widget(s_btn)
        block.height = h + 60
        return block

    def _show_spin(self):
        if self._spinner.parent is None:
            self.add_widget(self._spinner)

    def _hide_spin(self):
        if self._spinner.parent is not None:
            self.remove_widget(self._spinner)

    def _sync_bg(self, *_):
        self._bg.size = self.size
        self._bg.pos = self.pos

class MainScreenCus(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(245 / 255, 177 / 255, 67 / 255, 1)
            self._bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._sync_bg, pos=self._sync_bg)
        self._active = None
        root = BoxLayout(orientation='vertical')
        bar = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', padding=('10dp', '5dp'), spacing='10dp')
        self._title = Label(text='FOODY', color=(0, 0, 0, 1), halign="left", valign="middle", size_hint=(0.4, 1))
        self._title.bind(size=self._title.setter('text_size'))
        cog = MDIconButton(icon="cog", md_bg_color=(233 / 255, 150 / 255, 14 / 255, 1), icon_size="20sp")
        cog.bind(on_press=lambda *_: setattr(self.manager, 'current', 'settings'))
        bar.add_widget(self._title); bar.add_widget(cog)
        tabs = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        self._map = [("Menu", "menu"), ("Giỏ hàng", "cart"), ("Đơn hàng", "order"), ("Lịch sử", "history")]
        self._btns = []
        for txt, scr in self._map:
            b = RoundedButton(text=txt, size_hint=(.25, 1))
            b.change_color(233 / 255, 150 / 255, 14 / 255, 1); b.color = (0, 0, 0, 1)
            b.bind(on_press=lambda w, s=scr: self._switch(w, s))
            self._btns.append(b); tabs.add_widget(b)
        self.bind(size=self._resize)
        self._sm = ScreenManager(transition=FallOutTransition())
        self._sm.add_widget(MenuScreen(name="menu"))
        self._sm.add_widget(CartScreen(name="cart"))
        self._sm.add_widget(OrderScreen(name="order"))
        self._sm.add_widget(HistoryScreen(name="history"))
        root.add_widget(bar); root.add_widget(tabs); root.add_widget(self._sm)
        self.add_widget(root)
        if self._btns:
            self._switch(self._btns[0], "menu")

    def _switch(self, btn, scr):
        if self._active and self._active != btn:
            self._active.change_color(233 / 255, 150 / 255, 14 / 255, 1)
            self._active.color = (0, 0, 0, 1)
        btn.change_color(200 / 255, 100 / 255, 14 / 255, 1); btn.color = (0, 0, 0, 1)
        self._active = btn; self._sm.current = scr

    def _resize(self, *_):
        self._title.font_size = (self.width + self.height) / 50
        for b in self._btns:
            b.font_size = (self.width + self.height) / 72

    def _sync_bg(self, *_):
        self._bg.size = self.size; self._bg.pos = self.pos
