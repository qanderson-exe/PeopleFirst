from flask import Flask
from flask_restful import Api, Resource, fields, marshal_with, reqparse
from src.PeopleFirst.database.db import Database
from threading import Thread
#from src.PeopleFirst.recommender import recommend   # Currently commented out until we're ready to implement Echo


app = Flask(__name__)
db = Database()
api = Api(app)

forums_fields = {
    'icon': fields.String,
    'title': fields.String,
    'description': fields.String,
    "posts": fields.Integer,
    "last_active": fields.String,
    "tag": fields.String
}

resource_fields = {
    'id': fields.Integer,
    'link': fields.String,
    'webpage_title': fields.String
}

echo_fields = {
    'query': fields.String
}

forums_args = reqparse.RequestParser()
forums_args.add_argument('icon', type=str, required=False)
forums_args.add_argument('title', type=str, required=True, help='Title cannot be blank')
forums_args.add_argument('description', type=str, required=True, help='Description cannot be blank')
forums_args.add_argument('posts', type=int, required=True, help='Posts cannot be blank')
forums_args.add_argument('last_active', type=str, required=True, help='Last active cannot be blank')
forums_args.add_argument('tag', type=str, required=True, help='Tag cannot be blank')

post_args = reqparse.RequestParser()
post_args.add_argument('content', type=str, required=True, help='Content cannot be blank')
post_args.add_argument('author', type=str, required=True, help='Author cannot be blank')

reply_args = reqparse.RequestParser()
reply_args.add_argument('title', type=str, required=True, help='Title cannot be blank')
reply_args.add_argument('description', type=str, required=True, help='Description cannot be blank')

resource_args = reqparse.RequestParser()
resource_args.add_argument('link', type=str, required=True, help='Website link cannot be blank')
resource_args.add_argument('webpage_title', type=str, required=True, help='Webpage title cannot be blank')

echo_args = reqparse.RequestParser()
echo_args.add_argument('query', type=str, required=True, help='Chatbot query cannot be blank')

class ForumsAPI(Resource):
    @marshal_with(forums_fields)
    def get(self):
        forums = db.get_forums()
        return forums
    
    @marshal_with(forums_fields)
    def post(self):
        args = forums_args.parse_args()
        title = args['title']
        description = args['description']
        
        result = db.create_forum(title,description)
        return result, 201
    
class PostAPI(Resource):
    def get(self):
        posts = db.posts_collection.find({})
        return str(list(posts))

    def post(self):
        args = post_args.parse_args()
        forum_id = args['forum_id']
        content = args['content']
        author = args['author']
        result = db.create_post(forum_id,content,author)
        return result, 201
    
class ResourcesAPI(Resource):
    @marshal_with(resource_fields)
    def get(self):
        resources = db.get_resources()
        return resources
    
    @marshal_with(resource_fields)
    def get(self,id):
        resource = db.get_resource(id)
        return resource

    @marshal_with(resource_fields)
    def post(self):
        args = resource_args.parse_args()
        link = args['link']
        webpage_title = args['webpage title']
        result = db.create_resource(link,webpage_title)
        return result, 201

class UserAPI(Resource):
    def get(self):
        users = db.users_collection.find({})
        return str(list(users))

    def post(self):
        return "Not implemented", 201

class EchoAPI(Resource):
    """
    Server side receives queries from App UI, runs Echo on the server computer, and then returns the recommended source to the App
    """
    @marshal_with(echo_fields)
    def post(self):
        args = echo_args.parse_args()
        #recommendation = recommend(args)  # Currently commented out until we're ready to implement Echo
        #return recommendation, 201

def server_start():
    try:
        app.run(host='0.0.0.0', port=5000)
    except:
        pass

def run():
    try:
        t = Thread(target=server_start)
        t.start()
    except:
        pass

api.add_resource(ForumsAPI,'/api/forums/')
api.add_resource(PostAPI,'/api/posts/')
api.add_resource(UserAPI,'/api/users/')
api.add_resource(EchoAPI,'/api/echo/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)