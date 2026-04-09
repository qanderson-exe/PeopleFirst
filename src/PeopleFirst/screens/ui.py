from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from src.PeopleFirst.screens.forum_ui import ForumScreen


class PeopleFirstApp(App):
    def build(self):
        self.title = "PeopleFirst – Forums"
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(ForumScreen(name="forum",test_server=True))
        return sm