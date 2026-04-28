from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from src.PeopleFirst.screens.forum_ui import ForumScreen, ThreadScreen
from src.PeopleFirst.screens.echo_ui import EchoUI
from src.PeopleFirst.screens.resources_ui import ResourcesScreen



class PeopleFirstApp(App):
    def build(self):
        self.title = "PeopleFirst - College Student Mental Health"
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(ForumScreen(name="Forum"))
        sm.add_widget(EchoUI(name="Echo"))
        sm.add_widget(ThreadScreen(name="Thread"))
        sm.add_widget(ResourcesScreen(name="Resources"))
        return sm