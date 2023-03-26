from fastapi import FastAPI  # The fastAPI
from fastapi.params import Body  # For receiving data in post requests
from pydantic import BaseModel  # To specify a schema of what the post request data should look like
from typing import Optional  # In case we want to add some optional data a user may or may not send with POST request

app = FastAPI()


# POST request data schema
class Post(BaseModel):
	# Must provide this data
	title: str
	content: str
	# Optional. If not provided by user, set a default value or None
	published: bool = True
	rating: Optional[int] = None


# Path Operation
# Get request
@app.get("/")
def root():
	return {"message": "Hello"}


# Path Operation
# POST request
@app.post("/posts")
def create_post(post: Post):  # Receive data from post and validate it with the Post class schema
	print(post.title)
	print(post.content)
	print(post.published)
	print(post.rating)
	print(post.dict())
	
	return {"Data": f"{post}"}
