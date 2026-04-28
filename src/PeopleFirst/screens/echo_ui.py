from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.anchorlayout import AnchorLayout
import json
from kivy.network.urlrequest import UrlRequest


def get_color(color):
    match color:
        case "LIGHT_BG":
            return (0.95,0.90,0.79,1)
        case "HEADER_BG":
            return (0.07, 0.09, 0.11, 1)
        case "CARD_BG":
            return (0.10, 0.15, 0.18, 1)      # dark card surface
        case "TEAL_DARK":
            return (0.05, 0.27, 0.27, 1)      # header / accent fill
        case "TEAL_ACCENT":
            return (0.20, 0.70, 0.65, 1)      # bright accent / highlights
        case "TEXT_MUTED":
            return (0.38, 0.48, 0.48, 1)      # very muted
        case "TEXT_PRIMARY":
            return (0.93, 0.93, 0.90, 1)      # off-white primary text
        case "TEXT_SECONDARY":
            return (0.55, 0.68, 0.68, 1)      # muted teal-grey
        case "MESSAGE_COLOR":
            return (0, 0, 0, 1)
        case "ECHO_MESSAGE_BG":
            return (0.79, 0.87, 0.79, 1)
        case "USER_MESSAGE_BG":
            return (0.91, 0.85, 0.70, 1)


def make_label(text, font_size=14, color=get_color("TEXT_PRIMARY"), bold=False,
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

Builder.load_string('''
<Message>:
    size_hint: None, None
    size: self.texture_size[0] + 40, self.texture_size[1] + 20
    padding: [20, 10]
    canvas.before:
        Color:
            rgba: self.bg_color # Blue background
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [15, 15, 15, 15] # Rounded corners
''')

class Message(Label):
    def __init__(self, text, sender="Me", **kwargs):
        # Blue for 'me' (right), Gray for 'them' (left)
        self.bg_color = (0.1, 0.5, 0.9, 1) if sender == "Me" else (0.4, 0.4, 0.4, 1)
        super().__init__(text=text, **kwargs)

class CardLayout(BoxLayout):
    """BoxLayout with a rounded-rect card background."""
    def __init__(self, bg_color=get_color("CARD_BG"), radius=14, **kwargs):
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

class EchoUI(Screen):
    def __init__(self, ip='http://localhost:5000/api/echo/', **kwargs):
        super().__init__(**kwargs)
        self.IP = ip
        with self.canvas.before:
            Color(*get_color("LIGHT_BG"))
            self._rect = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=[dp(14)])
        self.bind(pos=self.update_background, size=self.update_background)
        self.build_ui()

    def update_background(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def build_ui(self):
        root = BoxLayout(orientation="vertical") 
        # ── Header bar
        root.add_widget(self.build_header())

        

        # ── Scrollable topic list
        self.scroll = ScrollView(do_scroll_x=False)
        self.messages = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.messages.bind(
            minimum_height=self.messages.setter('height')
        )

        wimg = Image(source='src/resources/Echo.png',size_hint_y = None)
        root.add_widget(wimg)
        self.scroll.add_widget(self.messages)
        
        root.add_widget(self.scroll)
        self.messages.add_widget(Message("Hi user! I'm Echo, your AI chatbot designed to help you navigate the app! What do you need help with?", sender="Echo"))
        input_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        self.message_input = TextInput(multiline=False, hint_text="Type a message...")
        send_button = Button(text="Send", size_hint=(0.2, 1))
        send_button.bind(on_release=lambda instance: self.add_message(instance, "Me"))
        
        input_layout.add_widget(self.message_input)
        input_layout.add_widget(send_button)
        root.add_widget(input_layout)
        root.add_widget(self.build_nav())
        self.add_widget(root)

        # self.messages.add_widget(make_label("Hi user! I'm Echo, your AI chatbot designed to help you navigate the app! What do you need help with?",font_size=16, color=MESSAGE_COLOR)))
        # root.add_widget(self.messages)
        
        # self.add_widget(root)

    # ── Header ────────────────────────────────────────────────────────────
    def build_header(self):
        header = CardLayout(
            bg_color=get_color("TEAL_DARK"),
            radius=0,
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            padding=[dp(14), 0, dp(14), 0],
            spacing=dp(1),
        )

        title = make_label("Echo - PeopleFirst AI Chatbot", font_size=22, bold=True,
                           color=get_color("TEXT_PRIMARY"), halign="center")
        
        header.add_widget(title)
        return header
    
    def add_message(self, instance=None, sender="Me"):
        # Wrap the bubble in an AnchorLayout to align it
        message = self.message_input.text.strip()
        side = 'right' if sender == "Me" else 'left'
        anchor = AnchorLayout(anchor_x=side, size_hint_y=None, height=50)
        bubble = Message(message, sender)

        # Ensure the anchor height matches the bubble height
        bubble.bind(height=lambda inst, val: setattr(anchor, 'height', val))
        
        anchor.add_widget(bubble)
        self.messages.add_widget(anchor)
        self.scroll.scroll_y = 0
        if sender == "Me":
            self.create_query()

    def create_query(self):
        query = {'query': self.message_input.text.strip()}
        self.message_input.text = ""
        params = json.dumps(query)
        request = UrlRequest(
            self.IP, 
            req_body=params,
            req_headers={'Content-Type': 'application/json'}, 
            on_success=self.on_success
        )
    
    def on_success(self, req, result):
        print("Query answered!:", result)
        message = "Your top recommended resources for your query were:\n\n"
        for index,recommendation in enumerate(result['query']):
            message += f'#{index+1}: {recommendation}\n'
        self.messages.add_widget(Message(message, sender='Echo'))

    # ── Bottom Nav ────────────────────────────────────────────────────────
    def build_nav(self):
        nav = CardLayout(
            bg_color=get_color("TEAL_DARK"),
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
            ("E", "Echo"),
            ("P", "Profile"),
        ]
        for icon, label in items:
            is_active = label == "Echo"
            col_box = BoxLayout(orientation="vertical", spacing=0)
            if label == "Resources" or label == "Forums":
                
                icon_lbl = Button(
                    text=f"[size=22]{icon}[/size]\n[size=9]{label}",
                    markup=True,
                    halign='center',
                    color=get_color("TEAL_ACCENT") if is_active else get_color("TEXT_MUTED"),
                    background_color = get_color("TEAL_DARK") if is_active else get_color("TEXT_MUTED")
                )
                
                if label == "Forums":
                    icon_lbl.bind(on_release= lambda instance: self.transition_screens("Forum"))
                else:
                    icon_lbl.bind(on_release= lambda instance: self.transition_screens("Resources"))
            else:
                icon_lbl = Label(
                    text=icon,
                    font_size=dp(22),
                    color=get_color("TEAL_ACCENT") if is_active else get_color("TEXT_MUTED"),
                )
                text_lbl = Label(
                    text=label,
                    font_size=dp(9),
                    bold=is_active,
                    color=get_color("TEAL_ACCENT") if is_active else get_color("TEXT_MUTED"),
                )
            col_box.add_widget(icon_lbl)
            if label != "Resources" and label != "Forums":
                col_box.add_widget(text_lbl)
            nav.add_widget(col_box)

        # Active indicator line
        return nav
    
    def transition_screens(self, screen_name):
        self.manager.transition.direction = 'right'
        self.manager.current = screen_name
    

class PeopleFirstApp(App):
    def build(self):
        self.title = "PeopleFirst – Echo"
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(EchoUI(name="Echo", test_server=True))
        return sm

if __name__ == '__main__':
    PeopleFirstApp().run()
