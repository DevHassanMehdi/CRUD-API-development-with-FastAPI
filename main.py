from fastapi import FastAPI  # The fastAPI
from pydantic import BaseModel  # To specify a schema of what the post request data should look like
from typing import Optional  # In case we want to add some optional data a user may or may not send with POST request
from random import randrange  # To temporarily create random Ids when working without database

app = FastAPI()


# POST request data schema
class Post(BaseModel):
	# Must provide this data
	title: str
	content: str
	# Optional. If not provided by user, set a default value or None
	published: bool = True
	rating: Optional[float] = None


my_posts = [
	{
		'title': 'this is the first post',
		'content': 'this is the content',
		'published': False,
		'rating': 2.4,
		"id": 54351},
	{
		'title': 'this is the second post',
		'content': 'this is the content',
		'published': False,
		'rating': 4.0,
		"id": 13876}]


def find_post(post_id):
	for post in my_posts:
		if post["id"] == post_id:
			return post


# Path Operation
# Get request
@app.get("/posts")
def get_all_posts():
	return {"data": my_posts}


# Find a specific post using the post id
@app.get("/posts/{post_id}")
def get_post(post_id: int):  # The post id should be int. FastAPI will auto convert string number into int
	post = find_post(post_id)
	return {"data": post}


# Path Operation
# POST request
@app.post("/posts")
def create_post(post: Post):  # Receive data from post and validate it with the Post class schema
	post_dict = post.dict()
	post_dict["id"] = randrange(1, 9999999)
	my_posts.append(post_dict)
	return {"Data": post_dict}
