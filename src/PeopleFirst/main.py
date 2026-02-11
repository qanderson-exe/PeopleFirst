from kivy.app import App

from kivy.uix.button import Button

class PeopleFirst(App):
    def build(self):
        return Button(text="Login", background_color=(0,0,1,1), font_size=12)
    pass



PeopleFirst().run()