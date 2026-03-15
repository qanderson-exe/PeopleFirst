from pymongo import MongoClient
import os
from bson.objectid import ObjectId

# This is the connection string for the MongoDB Atlas cluster.
MONGO_URI = "mongodb+srv://coonsbrysona:CwCGKMMOHdUgXIoV@peoplefirst.3uyiys9.mongodb.net/?appName=PeopleFirst"

client = MongoClient(MONGO_URI)

# Access the "peoplefirst" database in the MongoDB Atlas cluster.
db = client["peoplefirst"]

# Access collections associated with the "peoplefirst" database.
forums_collection = db["forums"]
posts_collection = db["posts"]
users_collection = db["users"]

# Create a forum in the "forums" collection with the specified title and description.
def create_forum(title, description):
    forum = {
        "title": title,
        "description": description
    }

    result = forums_collection.insert_one(forum)
    return str(result.inserted_id)

# Retrieve all forums from the "forums" collection and return them as a list.
def get_forums():
    return list(forums_collection.find())

# Create a post in the "posts" collection with the specified forum ID, content, and author.
def create_post(forum_id, content, author):
    post = {
        "forum_id": ObjectId(forum_id),
        "content": content,
        "author": author
    }

    result = posts_collection.insert_one(post)
    return str(result.inserted_id)

# Retrieve all posts associated with a specific forum ID from the "posts" collection and return them as a list.
def get_posts(forum_id):
    id = ObjectId(forum_id)
    return list(posts_collection.find({"forum_id": id}))