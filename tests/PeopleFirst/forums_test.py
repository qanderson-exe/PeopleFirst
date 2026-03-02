import src.PeopleFirst.forum



def test_post_creation(forums_data):
    """Tests the creation of a new Forum post"""

    title, body = forums_data

    # Expects create_new_post to return a Post object that has at the minimum title and body attributes
    post = forum.create_new_post(title,body)
    
    if post.title == title and post.body == body:
        assert True
    else:
        assert False

def test_forums_text_loader(forums_data):
    """Tests loading forums posts from a text file"""
    
    title, body = forums_data

    # Expects load_post to return a Post object that has at the minimum title and body attributes
    post = forum.load_post(title)

    if post.title == title and post.body == body:
        assert True
    else:
        assert False

    





