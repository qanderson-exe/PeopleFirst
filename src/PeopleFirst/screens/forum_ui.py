"""
PeopleFirst - Forum UI
Sprint 1: Forum screen matching the dark teal brand aesthetic.
Run with: python forum_ui.py
Requires: pip install kivy
"""

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
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior

# ── Brand Colors ─────────────────────────────────────────────────────────────
BG_DARK        = (0.07, 0.09, 0.11, 1)      # near-black background
CARD_BG        = (0.10, 0.15, 0.18, 1)      # dark card surface
TEAL_DARK      = (0.05, 0.27, 0.27, 1)      # header / accent fill
TEAL_MID       = (0.07, 0.38, 0.38, 1)      # button hover / tag bg
TEAL_ACCENT    = (0.20, 0.70, 0.65, 1)      # bright accent / highlights
LIME_ACCENT    = (0.72, 0.93, 0.30, 1)      # lime accent (from brand)
TEXT_PRIMARY   = (0.93, 0.93, 0.90, 1)      # off-white primary text
TEXT_SECONDARY = (0.55, 0.68, 0.68, 1)      # muted teal-grey
TEXT_MUTED     = (0.38, 0.48, 0.48, 1)      # very muted
DIVIDER        = (0.13, 0.20, 0.22, 1)      # subtle divider

# ── Window Setup ─────────────────────────────────────────────────────────────
Window.size = (390, 844)          # iPhone-like portrait viewport
Window.clearcolor = BG_DARK

# ── Sample Data ──────────────────────────────────────────────────────────────
FORUM_TOPICS = [
    {
        "icon": "💬",
        "title": "Anxiety & Stress Management",
        "desc": "Tips and support for managing academic anxiety and daily stress.",
        "posts": 143,
        "last_active": "11h ago",
        "tag": "Popular",
    },
    {
        "icon": "🫂",
        "title": "Depression Support",
        "desc": "A safe space to share your experiences and find understanding.",
        "posts": 140,
        "last_active": "2h ago",
        "tag": "Active",
    },
    {
        "icon": "📚",
        "title": "Academic Pressure & Burnout",
        "desc": "Dealing with grades, deadlines, and the pressure to succeed.",
        "posts": 56,
        "last_active": "4h ago",
        "tag": None,
    },
    {
        "icon": "🧘",
        "title": "Mindfulness & Self-Care",
        "desc": "Meditation, routines, and practices that help you recharge.",
        "posts": 53,
        "last_active": "2h ago",
        "tag": None,
    },
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def rgba(color):
    """Convert 0-1 tuple to 0-255 tuple for kivy Color instruction."""
    return color


class RoundedBox(Widget):
    """Invisible widget used purely to draw a rounded rect background."""
    def __init__(self, bg_color=CARD_BG, radius=14, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = radius
        with self.canvas.before:
            Color(*self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=[dp(self.radius)])
        self.bind(pos=self._update, size=self._update)

    def _update(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size


class CardLayout(BoxLayout):
    """BoxLayout with a rounded-rect card background."""
    def __init__(self, bg_color=CARD_BG, radius=14, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = radius
        with self.canvas.before:
            Color(*self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=[dp(self.radius)])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size


class ClickableCard(ButtonBehavior, BoxLayout):
    """A card that is fully clickable with press highlight — no overlay needed."""
    def __init__(self, bg_color=CARD_BG, radius=14, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self._bg_normal = bg_color
        self._bg_pressed = tuple(min(c + 0.06, 1.0) for c in bg_color[:3]) + (1,)
        self.radius = radius
        with self.canvas.before:
            self._color_inst = Color(*self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=[dp(self.radius)])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def on_press(self):
        self._color_inst.rgba = self._bg_pressed

    def on_release(self):
        self._color_inst.rgba = self._bg_normal


def make_label(text, font_size=14, color=TEXT_PRIMARY, bold=False,
               halign="left", valign="middle", size_hint_y=None, height=None):
    lbl = Label(
        text=text,
        font_size=dp(font_size),
        color=color,
        bold=bold,
        halign=halign,
        valign=valign,
        text_size=(None, None),
    )
    if size_hint_y is not None:
        lbl.size_hint_y = size_hint_y
    if height is not None:
        lbl.height = dp(height)
        lbl.size_hint_y = None
    lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
    return lbl


# ── Forum Screen ─────────────────────────────────────────────────────────────

class ForumScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._search_text = ""
        self._build_ui()

    # ── Build ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = BoxLayout(orientation="vertical")

        # ── Status bar spacer
        spacer = Widget(size_hint_y=None, height=dp(44))
        with spacer.canvas:
            Color(*TEAL_DARK)
            spacer._rect = Rectangle(pos=spacer.pos, size=spacer.size)
        spacer.bind(pos=lambda i, v: setattr(spacer._rect, 'pos', v),
                    size=lambda i, v: setattr(spacer._rect, 'size', v))
        root.add_widget(spacer)

        # ── Header bar
        root.add_widget(self._build_header())

        # ── Search bar
        root.add_widget(self._build_search())

        # ── Create Topic Button
        btn_wrap = BoxLayout(
            size_hint_y=None, height=dp(48),
            padding=[dp(12), dp(4), dp(12), dp(4)],
        )
        create_btn = ClickableCard(
            bg_color=TEAL_MID,
            radius=12,
            orientation="horizontal",
            padding=[dp(14), 0, dp(14), 0],
            spacing=dp(8),
        )
        create_btn.add_widget(Label(
            text="✏️",
            font_size=dp(16),
            size_hint=(None, 1),
            width=dp(24),
        ))
        create_btn.add_widget(Label(
            text="Don't see your topic? Create your own!",
            font_size=dp(13),
            bold=True,
            color=LIME_ACCENT,
            halign="left",
            valign="middle",
        ))
        create_btn.add_widget(Label(
            text="›",
            font_size=dp(20),
            color=LIME_ACCENT,
            size_hint=(None, 1),
            width=dp(20),
        ))
        create_btn.bind(on_release=self._show_new_topic_popup)
        btn_wrap.add_widget(create_btn)
        root.add_widget(btn_wrap)

        # ── Section label
        section_wrap = BoxLayout(
            size_hint_y=None, height=dp(36),
            padding=[dp(16), dp(4), dp(16), 0]
        )
        section_wrap.add_widget(
            make_label("Discussion Topics", font_size=12,
                       color=TEXT_SECONDARY, bold=True)
        )
        root.add_widget(section_wrap)

        # ── Scrollable topic list
        self.scroll = ScrollView(do_scroll_x=False)
        self.topic_grid = GridLayout(
            cols=1,
            spacing=dp(10),
            padding=[dp(12), dp(4), dp(12), dp(16)],
            size_hint_y=None,
        )
        self.topic_grid.bind(
            minimum_height=self.topic_grid.setter('height')
        )
        self._populate_topics(FORUM_TOPICS)
        self.scroll.add_widget(self.topic_grid)
        root.add_widget(self.scroll)

        # ── Welcome description at bottom
        footer_wrap = BoxLayout(
            size_hint_y=None, height=dp(100),
            padding=[dp(16), dp(8), dp(16), dp(12)],
        )
        footer_lbl = Label(
            text="[i]Welcome to the PeopleFirst Forum! This is a safe, supportive space for students to share, connect, and find comfort in knowing they're not alone. Whether you're going through a tough time or just looking for advice, we're here for you. Please keep in mind that all discussions are moderated to ensure a respectful environment — offensive language, hate speech, and harassment are not tolerated. Be kind, as everyone here is going through something, and remember that your identity remains anonymous at all times. If you are experiencing a crisis, please contact your campus counseling center or call 988 (Suicide & Crisis Lifeline).[/i]",
            font_size=dp(9),
            color=TEXT_MUTED,
            halign="center",
            valign="top",
            markup=True,
        )
        footer_lbl.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))
        footer_wrap.add_widget(footer_lbl)
        root.add_widget(footer_wrap)

        # ── Bottom nav
        root.add_widget(self._build_nav())

        self.add_widget(root)

    # ── Header ────────────────────────────────────────────────────────────
    def _build_header(self):
        header = CardLayout(
            bg_color=TEAL_DARK,
            radius=0,
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            padding=[dp(14), 0, dp(14), 0],
            spacing=dp(8),
        )

        back_btn = Button(
            text="←",
            font_size=dp(22),
            color=TEXT_PRIMARY,
            background_color=(0, 0, 0, 0),
            size_hint=(None, 1),
            width=dp(36),
        )
        back_btn.bind(on_release=lambda *_: None)

        title = make_label("Forums", font_size=18, bold=True,
                           color=TEXT_PRIMARY, halign="center")

        header.add_widget(back_btn)
        header.add_widget(title)
        return header

    # ── Search ────────────────────────────────────────────────────────────
    def _build_search(self):
        wrap = BoxLayout(
            size_hint_y=None, height=dp(54),
            padding=[dp(12), dp(8), dp(12), dp(4)],
        )
        field_wrap = CardLayout(
            bg_color=(0.12, 0.18, 0.21, 1),
            radius=24,
            orientation="horizontal",
            padding=[dp(12), 0, dp(12), 0],
            spacing=dp(6),
        )
        icon = Label(
            text="🔍",
            font_size=dp(16),
            size_hint=(None, 1),
            width=dp(24),
        )
        self.search_input = TextInput(
            hint_text="Search discussions…",
            hint_text_color=TEXT_MUTED,
            foreground_color=TEXT_PRIMARY,
            background_color=(0, 0, 0, 0),
            cursor_color=TEAL_ACCENT,
            font_size=dp(14),
            multiline=False,
            padding=[0, dp(10)],
        )
        self.search_input.bind(text=self._on_search)
        field_wrap.add_widget(icon)
        field_wrap.add_widget(self.search_input)
        wrap.add_widget(field_wrap)
        return wrap

    # ── Topic Card ────────────────────────────────────────────────────────
    def _build_topic_card(self, topic):
        card = ClickableCard(
            bg_color=CARD_BG,
            radius=14,
            orientation="horizontal",
            size_hint_y=None,
            height=dp(90),
            padding=[dp(14), dp(12), dp(14), dp(12)],
            spacing=dp(10),
        )
        card.bind(on_release=lambda *_, t=topic: self._open_topic(t))

        # Icon bubble
        icon_box = CardLayout(
            bg_color=TEAL_DARK,
            radius=10,
            size_hint=(None, None),
            size=(dp(44), dp(44)),
        )
        icon_lbl = Label(
            text=topic["icon"],
            font_size=dp(22),
        )
        icon_box.add_widget(icon_lbl)

        # Text column
        text_col = BoxLayout(orientation="vertical", spacing=dp(2))

        # Title row
        title_row = BoxLayout(orientation="horizontal", spacing=dp(6),
                              size_hint_y=None, height=dp(22))
        title_lbl = Label(
            text=topic["title"],
            font_size=dp(14),
            bold=True,
            color=TEXT_PRIMARY,
            halign="left",
            valign="middle",
            text_size=(None, None),
        )
        title_lbl.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))
        title_row.add_widget(title_lbl)

        if topic.get("tag"):
            tag = CardLayout(
                bg_color=TEAL_MID,
                radius=8,
                size_hint=(None, None),
                size=(dp(60), dp(18)),
            )
            tag_lbl = Label(
                text=topic["tag"],
                font_size=dp(9),
                bold=True,
                color=LIME_ACCENT,
            )
            tag.add_widget(tag_lbl)
            title_row.add_widget(tag)

        # Description
        desc_lbl = Label(
            text=topic["desc"],
            font_size=dp(11),
            color=TEXT_SECONDARY,
            halign="left",
            valign="top",
            text_size=(None, None),
        )
        desc_lbl.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))

        # Meta row
        meta_row = BoxLayout(orientation="horizontal",
                             size_hint_y=None, height=dp(16))
        posts_lbl = Label(
            text=f"💬 {topic['posts']} posts",
            font_size=dp(10),
            color=TEXT_MUTED,
            halign="left",
            valign="middle",
        )
        posts_lbl.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))
        active_lbl = Label(
            text=f"🕐 {topic['last_active']}",
            font_size=dp(10),
            color=TEXT_MUTED,
            halign="right",
            valign="middle",
        )
        active_lbl.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))
        meta_row.add_widget(posts_lbl)
        meta_row.add_widget(active_lbl)

        text_col.add_widget(title_row)
        text_col.add_widget(desc_lbl)
        text_col.add_widget(meta_row)

        # Chevron
        chevron = Label(
            text="›",
            font_size=dp(24),
            color=TEAL_ACCENT,
            size_hint=(None, 1),
            width=dp(20),
        )

        card.add_widget(icon_box)
        card.add_widget(text_col)
        card.add_widget(chevron)

        return card

    # ── Populate / Filter ─────────────────────────────────────────────────
    def _populate_topics(self, topics):
        self.topic_grid.clear_widgets()
        for topic in topics:
            self.topic_grid.add_widget(self._build_topic_card(topic))

    def _on_search(self, instance, value):
        query = value.strip().lower()
        filtered = [t for t in FORUM_TOPICS
                    if query in t["title"].lower() or query in t["desc"].lower()]
        self._populate_topics(filtered)

    # ── New Topic Popup ───────────────────────────────────────────────────
    def _show_new_topic_popup(self, *_):
        content = BoxLayout(orientation="vertical", spacing=dp(12),
                            padding=dp(16))

        content.add_widget(make_label("Create New Discussion",
                                      font_size=16, bold=True,
                                      color=TEXT_PRIMARY,
                                      size_hint_y=None, height=30))

        title_input = TextInput(
            hint_text="Topic title…",
            hint_text_color=TEXT_MUTED,
            foreground_color=TEXT_PRIMARY,
            background_color=(0.12, 0.18, 0.21, 1),
            cursor_color=TEAL_ACCENT,
            font_size=dp(13),
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            padding=[dp(10), dp(10)],
        )
        desc_input = TextInput(
            hint_text="What's on your mind? (anonymous)",
            hint_text_color=TEXT_MUTED,
            foreground_color=TEXT_PRIMARY,
            background_color=(0.12, 0.18, 0.21, 1),
            cursor_color=TEAL_ACCENT,
            font_size=dp(13),
            size_hint_y=None,
            height=dp(90),
            padding=[dp(10), dp(10)],
        )

        btn_row = BoxLayout(orientation="horizontal", spacing=dp(10),
                            size_hint_y=None, height=dp(42))

        cancel_btn = Button(
            text="Cancel",
            font_size=dp(13),
            color=TEXT_SECONDARY,
            background_color=CARD_BG,
        )

        post_btn = Button(
            text="Post",
            font_size=dp(13),
            bold=True,
            color=(0.05, 0.09, 0.09, 1),
            background_color=TEAL_ACCENT,
        )

        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(post_btn)

        content.add_widget(title_input)
        content.add_widget(desc_input)
        content.add_widget(btn_row)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.88, None),
            height=dp(300),
            background_color=TEAL_DARK,
            separator_height=0,
        )
        cancel_btn.bind(on_release=popup.dismiss)
        post_btn.bind(on_release=lambda *_: self._post_topic(
            title_input.text, desc_input.text, popup))
        popup.open()

    def _post_topic(self, title, desc, popup):
        if not title.strip():
            return
        new_topic = {
            "icon": "🆕",
            "title": title.strip(),
            "desc": desc.strip() or "No description provided.",
            "posts": 1,
            "last_active": "just now",
            "tag": "New",
        }
        FORUM_TOPICS.insert(0, new_topic)
        self._populate_topics(FORUM_TOPICS)
        popup.dismiss()

    def _open_topic(self, topic):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        content.add_widget(make_label(topic["title"], font_size=15, bold=True,
                                      color=TEXT_PRIMARY, size_hint_y=None, height=30))
        content.add_widget(make_label(topic["desc"], font_size=12,
                                      color=TEXT_SECONDARY, size_hint_y=None, height=40))
        content.add_widget(make_label(f"💬 {topic['posts']} posts  •  🕐 {topic['last_active']}",
                                      font_size=11, color=TEXT_MUTED,
                                      size_hint_y=None, height=24))
        close_btn = Button(
            text="Close",
            font_size=dp(13),
            color=(0.05, 0.09, 0.09, 1),
            background_color=TEAL_ACCENT,
            size_hint_y=None,
            height=dp(40),
        )
        content.add_widget(close_btn)
        popup = Popup(
            title="",
            content=content,
            size_hint=(0.88, None),
            height=dp(220),
            background_color=TEAL_DARK,
            separator_height=0,
        )
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    # ── Bottom Nav ────────────────────────────────────────────────────────
    def _build_nav(self):
        nav = CardLayout(
            bg_color=TEAL_DARK,
            radius=0,
            orientation="horizontal",
            size_hint_y=None,
            height=dp(64),
            padding=[0, dp(4), 0, dp(4)],
        )
        items = [
            ("H", "Home"),
            ("F", "Forums"),
            ("R", "Resources"),
            ("P", "Profile"),
        ]
        for icon, label in items:
            is_active = label == "Forums"
            col_box = BoxLayout(orientation="vertical", spacing=0)
            icon_lbl = Label(
                text=icon,
                font_size=dp(22),
                color=TEAL_ACCENT if is_active else TEXT_MUTED,
            )
            text_lbl = Label(
                text=label,
                font_size=dp(9),
                bold=is_active,
                color=TEAL_ACCENT if is_active else TEXT_MUTED,
            )
            col_box.add_widget(icon_lbl)
            col_box.add_widget(text_lbl)
            nav.add_widget(col_box)

        # Active indicator line
        return nav


# ── App Entry ─────────────────────────────────────────────────────────────────

class PeopleFirstApp(App):
    def build(self):
        self.title = "PeopleFirst – Forums"
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(ForumScreen(name="forum"))
        return sm


if __name__ == "__main__":
    PeopleFirstApp().run()
