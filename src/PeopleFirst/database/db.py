from pymongo import MongoClient
import os
from bson.objectid import ObjectId
from src.PeopleFirst.chatbot.summarizer import summarize_url

class Database():

    def __init__(self):
        # This is the connection string for the MongoDB Atlas cluster.
        self.MONGO_URI = "mongodb+srv://coonsbrysona:CwCGKMMOHdUgXIoV@peoplefirst.3uyiys9.mongodb.net/?appName=PeopleFirst"

        self.client = MongoClient(self.MONGO_URI)

        # Access the "peoplefirst" database in the MongoDB Atlas cluster.
        self.db = self.client["peoplefirst"]

        # Access collections associated with the "peoplefirst" database.
        self.forums_collection = self.db["forums"]
        self.posts_collection = self.db["posts"]
        self.users_collection = self.db["users"]
        self.replies_collection = self.db["replies"]
        self.resources_collection = self.db["resources"]
        self.check_resource_summary()

    def check_resource_summary(self):
        for resource in self.resources_collection.find({}):
            if not resource.get('summary'):
                try:
                    summary = summarize_url(resource['link'],sentence_count=5)
                    self.resources_collection.update_one({"_id":resource["_id"]}, {"$set": {"summary":summary}})
                    print(resource['link'], summary)
                except:
                    self.resources_collection.update_one({"_id":resource["_id"]}, {"$set": {"summary":"Summary of resource is currently unavailable"}})
    # Create a forum in the "forums" collection with the specified title and description.
    def create_forum(self,title, description):
        forum = {
            "title": title,
            "description": description,
            "is_reported": False
        }

        result = self.forums_collection.insert_one(forum)
        return str(result.inserted_id)
    
    # Allows a user to change the status of a forum
    def update_forum(self,dict_args,id):
        forum = dict_args
        result = self.forums_collection.replace_one({'forum_id':id}, forum)
        return str(result.upsertedId)

    # Retrieve all forums from the "forums" collection and return them as a list.
    def get_forums(self):
        return list(self.forums_collection.find())
    
    # Retrieve forum by id
    def get_forum(self,id):
        return self.forums_collection.find({"forum_id": id})

    # Create a post in the "posts" collection with the specified forum ID, content, and author.
    def create_post(self,forum_id, content, author):
        post = {
            "forum_id": ObjectId(forum_id),
            "content": content,
            "author": author
        }

        result = self.posts_collection.insert_one(post)
        return str(result.inserted_id)

    # Retrieve all posts associated with a specific forum ID from the "posts" collection and return them as a list.
    def get_posts(self,forum_id):
        id = ObjectId(forum_id)
        return list(self.posts_collection.find({"forum_id": id}))

    # Create a reply under a forum with a specific forum ID.
    def create_reply(self, forum_id, description):
        reply = {
            "forum_id": ObjectId(forum_id),
            "description": description
        }
        result = self.replies_collection.insert_one(reply)
        return str(result.inserted_id)

    # Retrieve all replies under a specific forum ID.
    def get_replies(self, forum_id):
        forum_object_id = ObjectId(forum_id)
        return list(self.replies_collection.find({"forum_id": forum_object_id}))
    
    # Create a new resource with a given link and webpage title.
    def create_resource(self,link,webpage_title):
        resource = {
            "resource_id": self.resources_collection.count_documents({}),
            "link": link,
            "webpage_title": webpage_title
        }
        result = self.resources_collection.insert_one(resource)
        return str(result.inserted_id)

    # Retrieve a resource by its unique id
    def get_resource(self,resource_id):
        id = ObjectId(resource_id)
        return self.resources_collection.find({"_id": id})
    
    # Retrieve a list of all resources in the database
    def get_resources(self):
        return list(self.resources_collection.find({}))
    

if __name__ == "__main__":
    db = Database()