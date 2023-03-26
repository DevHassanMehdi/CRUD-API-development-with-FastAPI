from fastapi import FastAPI  # The fastAPI
from fastapi.params import Body  # For receiving data in post requests
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
	{'title': 'this is the first post',
		'content': 'this is the content',
		'published': False,
		'rating': 2.4,
		"id": 54351},
	{'title': 'this is the second post',
		'content': 'this is the content',
		'published': False,
		'rating': 4.0,
		"id": 13876}]


# Path Operation
# Get request
@app.get("/posts")
def root():
	return {"data": my_posts}


# Path Operation
# POST request
@app.post("/posts")
def create_post(post: Post):  # Receive data from post and validate it with the Post class schema
	post_dict = post.dict()
	post_dict["id"] = randrange(1, 9999999)
	my_posts.append(post_dict)
	return {"Data": post_dict}
