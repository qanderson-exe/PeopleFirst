from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.network.urlrequest import UrlRequest
import webbrowser


def get_color(color):
    match color:
        case "BG_DARK":    return (0.07, 0.09, 0.11, 1)
        case "CARD_BG":    return (0.10, 0.15, 0.18, 1)
        case "TEAL_DARK":  return (0.05, 0.27, 0.27, 1)
        case "TEAL_MID":   return (0.07, 0.38, 0.38, 1)
        case "TEAL_ACCENT":return (0.20, 0.70, 0.65, 1)
        case "LIME_ACCENT":return (0.72, 0.93, 0.30, 1)
        case "TEXT_PRIMARY":   return (0.93, 0.93, 0.90, 1)
        case "TEXT_SECONDARY": return (0.55, 0.68, 0.68, 1)
        case "TEXT_MUTED":     return (0.38, 0.48, 0.48, 1)
        case "DIVIDER":        return (0.13, 0.20, 0.22, 1)


class CardLayout(BoxLayout):
    def __init__(self, bg_color=None, radius=14, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color or get_color("CARD_BG")
        with self.canvas.before:
            Color(*self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(radius)])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size


class ClickableCard(ButtonBehavior, BoxLayout):
    def __init__(self, bg_color=None, radius=14, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color or get_color("CARD_BG")
        self._bg_normal = self.bg_color
        self._bg_pressed = tuple(min(c + 0.06, 1.0) for c in self.bg_color[:3]) + (1,)
        with self.canvas.before:
            self._color_inst = Color(*self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(radius)])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def on_press(self):   self._color_inst.rgba = self._bg_pressed
    def on_release(self): self._color_inst.rgba = self._bg_normal


def make_label(text, font_size=14, color=None, bold=False,
               halign="left", valign="middle", size_hint_y=None, height=None):
    lbl = Label(text=text, font_size=dp(font_size),
                color=color or get_color("TEXT_PRIMARY"),
                bold=bold, halign=halign, valign=valign, text_size=(None, None))
    if size_hint_y is not None: lbl.size_hint_y = size_hint_y
    if height is not None:
        lbl.height = dp(height)
        lbl.size_hint_y = None
    lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
    return lbl


class ResourcesScreen(Screen):
    """
    Displays approved help resources from GET /api/resources/
    Resource fields: id (int), link (str), webpage_title (str)
    """

    def __init__(self, ip="http://localhost:5000/api/resources/", **kwargs):
        super().__init__(**kwargs)
        self.IP = ip
        self.RESOURCES = []
        self._search_text = ""
        with self.canvas.before:
            Window.size = (390, 844)
            Color(*get_color("BG_DARK"))
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=self._update_bg, size=self._update_bg)
        self._build_ui()

    def _update_bg(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _build_ui(self):
        root = BoxLayout(orientation="vertical")

        # Status bar spacer
        spacer = Widget(size_hint_y=None, height=dp(44))
        with spacer.canvas:
            Color(*get_color("TEAL_DARK"))
            spacer._rect = Rectangle(pos=spacer.pos, size=spacer.size)
        spacer.bind(pos=lambda i, v: setattr(spacer._rect, 'pos', v),
                    size=lambda i, v: setattr(spacer._rect, 'size', v))
        root.add_widget(spacer)
        root.add_widget(self._build_header())
        root.add_widget(self._build_search())

        # Section label
        section_wrap = BoxLayout(size_hint_y=None, height=dp(36),
                                 padding=[dp(16), dp(4), dp(16), 0])
        section_wrap.add_widget(make_label("Approved Resources", font_size=12,
                                           color=get_color("TEXT_SECONDARY"), bold=True))
        root.add_widget(section_wrap)

        # Scrollable list
        self.scroll = ScrollView(do_scroll_x=False)
        self.resource_grid = GridLayout(cols=1, spacing=dp(10),
                                        padding=[dp(12), dp(4), dp(12), dp(16)],
                                        size_hint_y=None)
        self.resource_grid.bind(minimum_height=self.resource_grid.setter('height'))
        self._show_loading()

        db_request = self._get_request()
        db_request.wait()
        result = db_request.result
        self.RESOURCES = [r for r in result if isinstance(r, dict)] if isinstance(result, list) else []
        self._populate_resources(self.RESOURCES)

        self.scroll.add_widget(self.resource_grid)
        root.add_widget(self.scroll)
        root.add_widget(self._build_footer())
        root.add_widget(self._build_nav())
        self.add_widget(root)

    def _build_header(self):
        header = CardLayout(bg_color=get_color("TEAL_DARK"), radius=0,
                            orientation="horizontal", size_hint_y=None, height=dp(56),
                            padding=[dp(14), 0, dp(14), 0], spacing=dp(8))
        back_btn = Button(text="←", font_size=dp(22), color=get_color("TEXT_PRIMARY"),
                          background_color=(0, 0, 0, 0), size_hint=(None, 1), width=dp(36))
        back_btn.bind(on_release=lambda *_: None)
        header.add_widget(back_btn)
        header.add_widget(make_label("Resources", font_size=18, bold=True,
                                     color=get_color("TEXT_PRIMARY"), halign="center"))
        return header

    def _build_search(self):
        wrap = BoxLayout(size_hint_y=None, height=dp(54),
                         padding=[dp(12), dp(8), dp(12), dp(4)])
        field_wrap = CardLayout(bg_color=(0.12, 0.18, 0.21, 1), radius=24,
                                orientation="horizontal",
                                padding=[dp(12), 0, dp(12), 0], spacing=dp(6))
        field_wrap.add_widget(Label(text="🔍", font_size=dp(16),
                                    size_hint=(None, 1), width=dp(24)))
        self.search_input = TextInput(
            hint_text="Search resources…",
            hint_text_color=get_color("TEXT_MUTED"),
            foreground_color=get_color("TEXT_PRIMARY"),
            background_color=(0, 0, 0, 0),
            cursor_color=get_color("TEAL_ACCENT"),
            font_size=dp(14), multiline=False, padding=[0, dp(10)])
        self.search_input.bind(text=self._on_search)
        field_wrap.add_widget(self.search_input)
        wrap.add_widget(field_wrap)
        return wrap

    def _build_resource_card(self, resource):
        """
        Card layout for a resource.
        API fields used: webpage_title, link
        """
        card = ClickableCard(bg_color=get_color("CARD_BG"), radius=14,
                             orientation="horizontal", size_hint_y=None, height=dp(80),
                             padding=[dp(14), dp(12), dp(14), dp(12)], spacing=dp(10))
        card.bind(on_release=lambda *_, r=resource: self._open_resource(r))

        # Icon bubble
        icon_box = CardLayout(bg_color=get_color("TEAL_DARK"), radius=10,
                              size_hint=(None, None), size=(dp(44), dp(44)))
        icon_box.add_widget(Label(text="🔗", font_size=dp(22)))

        # Text column
        text_col = BoxLayout(orientation="vertical", spacing=dp(4))

        title_lbl = Label(text=resource.get("webpage_title", "Untitled Resource"),
                          font_size=dp(14), bold=True, color=get_color("TEXT_PRIMARY"),
                          halign="left", valign="middle", text_size=(None, None))
        title_lbl.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))

        link_lbl = Label(text=resource.get("link", ""),
                         font_size=dp(11), color=get_color("TEAL_ACCENT"),
                         halign="left", valign="middle", text_size=(None, None))
        link_lbl.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))

        text_col.add_widget(title_lbl)
        text_col.add_widget(link_lbl)

        # Chevron
        chevron = Label(text="›", font_size=dp(24), color=get_color("TEAL_ACCENT"),
                        size_hint=(None, 1), width=dp(20))

        card.add_widget(icon_box)
        card.add_widget(text_col)
        card.add_widget(chevron)
        return card

    def _populate_resources(self, resources):
        self.resource_grid.clear_widgets()
        if not resources:
            self.resource_grid.add_widget(
                make_label("No resources found.", font_size=13,
                           color=get_color("TEXT_MUTED"), halign="center",
                           size_hint_y=None, height=60))
            return
        for resource in resources:
            self.resource_grid.add_widget(self._build_resource_card(resource))

    def _on_search(self, instance, value):
        query = value.strip().lower()
        filtered = [r for r in self.RESOURCES
                    if query in r.get("webpage_title", "").lower()
                    or query in r.get("link", "").lower()]
        self._populate_resources(filtered)

    def _show_loading(self):
        self.resource_grid.clear_widgets()
        self.resource_grid.add_widget(
            make_label("Loading resources…", font_size=13,
                       color=get_color("TEXT_MUTED"), halign="center",
                       size_hint_y=None, height=60))

    def _open_resource(self, resource):
        content = BoxLayout(orientation="vertical", spacing=dp(14),
                            padding=[dp(16), dp(16), dp(16), dp(16)])

        top_row = BoxLayout(orientation="horizontal", spacing=dp(10),
                            size_hint_y=None, height=dp(48))
        top_row.add_widget(Label(text="🔗", font_size=dp(28),
                                 size_hint=(None, 1), width=dp(40)))
        top_row.add_widget(make_label(resource.get("webpage_title", "Resource"),
                                      font_size=15, bold=True,
                                      color=get_color("TEXT_PRIMARY")))
        content.add_widget(top_row)

        link_lbl = make_label(resource.get("link", ""), font_size=11,
                              color=get_color("TEAL_ACCENT"),
                              size_hint_y=None, height=20)
        content.add_widget(link_lbl)
        content.add_widget(Widget())  # spacer

        open_btn = Button(text="Open Resource  ›", font_size=dp(13), bold=True,
                          color=(0.05, 0.09, 0.09, 1),
                          background_color=get_color("TEAL_ACCENT"),
                          size_hint_y=None, height=dp(44))
        close_btn = Button(text="Close", font_size=dp(12),
                           color=get_color("TEXT_SECONDARY"),
                           background_color=(0.12, 0.18, 0.21, 1),
                           size_hint_y=None, height=dp(38))

        popup = Popup(title="", content=content, size_hint=(0.88, None), height=dp(280),
                      background_color=get_color("CARD_BG"), separator_height=0)
        open_btn.bind(on_release=lambda *_: webbrowser.open(resource.get("link", "")))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(open_btn)
        content.add_widget(close_btn)
        popup.open()

    def _get_request(self):
        return UrlRequest(self.IP, on_success=self._on_success,
                          on_error=self._on_error, on_failure=self._on_error)

    def _on_success(self, req, result):
        self.RESOURCES = [r for r in result if isinstance(r, dict)] if isinstance(result, list) else []
        self._populate_resources(self.RESOURCES)

    def _on_error(self, *_):
        self.resource_grid.clear_widgets()
        self.resource_grid.add_widget(
            make_label("Could not load resources. Please try again later.",
                       font_size=12, color=get_color("TEXT_MUTED"),
                       halign="center", size_hint_y=None, height=60))

    def _build_footer(self):
        footer_wrap = BoxLayout(size_hint_y=None, height=dp(80),
                                padding=[dp(16), dp(8), dp(16), dp(12)])
        footer_lbl = Label(
            text="[i]These resources have been reviewed and approved by the PeopleFirst team. If you are experiencing a crisis, please call or text 988 (Suicide & Crisis Lifeline) immediately.[/i]",
            font_size=dp(9), color=get_color("TEXT_MUTED"),
            halign="center", valign="top", markup=True)
        footer_lbl.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))
        footer_wrap.add_widget(footer_lbl)
        return footer_wrap

    def _build_nav(self):
        nav = CardLayout(bg_color=get_color("TEAL_DARK"), radius=0,
                         orientation="horizontal", size_hint_y=None, height=dp(64),
                         padding=[0, dp(4), 0, dp(4)])
        for icon, label in [("H","Home"),("F","Forums"),("R","Resources"),("E","Echo"),("P","Profile")]:
            is_active = (label == "Resources")
            col = BoxLayout(orientation="vertical", spacing=0)
            col.add_widget(Label(text=icon, font_size=dp(22),
                                 color=get_color("TEAL_ACCENT") if is_active else get_color("TEXT_MUTED")))
            col.add_widget(Label(text=label, font_size=dp(9), bold=is_active,
                                 color=get_color("TEAL_ACCENT") if is_active else get_color("TEXT_MUTED")))
            nav.add_widget(col)
        return nav


class ResourcesApp(App):
    def build(self):
        self.title = "PeopleFirst – Resources"
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(ResourcesScreen(name="resources"))
        return sm


if __name__ == "__main__":
    ResourcesApp().run()
