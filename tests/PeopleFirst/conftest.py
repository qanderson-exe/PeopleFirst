import pytest

@pytest.fixture(scope="session")
def forums_data():
    """Stores the global variables needed for forums test scripts"""

    title = "Juggling work and school"
    body = "Hi, I've been struggling a lot lately with coming home for classes and jumping straight into my job. It's been leaving me with little time to do any homework or studying " \
    "and even less time for hanging out with my friends. I've been really stressed out and don't know what to do"

    return title,body