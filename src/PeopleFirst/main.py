import os
os.environ["KIVY_LOG_LEVEL"] = "warning"

import logging
logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("pymongo.topology").setLevel(logging.WARNING)
logging.getLogger("pymongo.connection").setLevel(logging.WARNING)

from src.PeopleFirst.screens.ui import PeopleFirstApp


def main():
    PeopleFirstApp().run()

if __name__ == "__main__":  
    main()
