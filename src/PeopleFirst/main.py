import os
os.environ["KIVY_LOG_LEVEL"] = "warning"

import logging
logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("pymongo.topology").setLevel(logging.WARNING)
logging.getLogger("pymongo.connection").setLevel(logging.WARNING)

from kivy.app import App
from kivy.uix.button import Button

import database.db as db

class PeopleFirst(App):
    def build(self):
        btn = Button(
            text="Login",
            background_color=(0, 0, 1, 1),
            font_size=12
        )

        btn.bind(on_press=self.handle_example_database_operations)
        return btn
    
    def handle_example_database_operations(self, instance):
        # Example usage of database functions
        db.create_forum("Anxiety Support", "Discuss anxiety and coping strategies.")
        forums = db.get_forums()
        for forum in forums:
            print(forum)

        db.create_post("69b7419881ef391290364bb3", "This is a post about anxiety.", "User123")
        posts = db.get_posts("69b7419881ef391290364bb3")
        for post in posts:
            print(post)
            
            post_id = str(post['_id'])
            
            db.create_reply(post_id, "I feel the anxiety the same way", "User456")
            replies = db.get_replies(post_id)
            for reply in replies:
                print(reply)

if __name__ == "__main__":  
    PeopleFirst().run()
