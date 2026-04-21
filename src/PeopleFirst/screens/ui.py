from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from src.PeopleFirst.screens.forum_ui import ForumScreen
from src.PeopleFirst.screens.echo_ui import EchoUI



class PeopleFirstApp(App):
    def build(self):
        self.title = "PeopleFirst – Forums"
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(ForumScreen(name="Forum"))
        sm.add_widget(EchoUI(name="Echo"))
        return sm