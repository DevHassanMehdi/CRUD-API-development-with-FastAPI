from fastapi import FastAPI  # The fastAPI
from pydantic import BaseModel  # To specify a schema of what the post request data should look like
from fastapi import HTTPException, Response, status  # To raise appropriate HTTP Exception and set http status
import psycopg2  # Library to deal with our Postgres database
from psycopg2.extras import RealDictCursor  # To get the column names when we return something from the database
import time  # To add time pause between connection failing and retry connecting to the database

app = FastAPI()


# POST request data schema
class Post(BaseModel):
	# Must provide this data
	title: str
	content: str
	# Optional. If not provided by user, set a default value or None
	published: bool = True


# Connect to our postgres database
while True:
	try:
		# Connection arguments
		connection = psycopg2.connect(
			host='localhost', database='fastapi', user='postgres', password='root', cursor_factory=RealDictCursor)
		cursor = connection.cursor()  # Used to execute SQL queries
		print("Connection Successful")
		break
	except Exception as error:
		# If connection fails, print the error and retry to connect every 2 seconds
		print("Error:", error)
		time.sleep(2)

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


# A method to find the specific post requested by user in get request by id
def find_post(post_id):
	for post in my_posts:
		if post["id"] == post_id:
			return post


# A method to find the specific post and return its index
def find_post_index(post_id):
	for index, post in enumerate(my_posts):
		if post['id'] == post_id:
			return index


# Path Operations

# Create a post
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):  # Receive data from post and validate it with the Post class schema
	print(post)
	cursor.execute(
		"""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
		(post.title, post.content, post.published))
	new_post = cursor.fetchone()
	connection.commit()
	
	return {"Data": new_post}


# Get all posts
@app.get("/posts", status_code=status.HTTP_200_OK)
def get_all_posts():
	cursor.execute("""SELECT * FROM posts""")
	posts = cursor.fetchall()
	return {"data": posts}


# Find the latest post
@app.get("/posts/latest", status_code=status.HTTP_200_OK)
def get_latest_post():
	cursor.execute("""SELECT * FROM posts ORDER BY id DESC LIMIT 1""")
	post = cursor.fetchone()
	if not post:  # If item not found set http status to 404
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No posts yet.")
	return {"data": post}


# Find a specific post using the post id
@app.get("/posts/{post_id}", status_code=status.HTTP_200_OK)
def get_post(post_id):  # The post id should be int.
	cursor.execute("""SELECT * FROM posts WHERE id = %s""", post_id)
	post = cursor.fetchone()
	if not post:  # If item not found set http status to 404
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No posts yet.")
	return {"data": post}


# Update Post
@app.put("/posts/{post_id}")
def update_post(post_id: int, post: Post):
	index = find_post_index(post_id)
	if index is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
	post_dict = post.dict()
	post_dict["id"] = post_id
	my_posts[index] = post_dict
	return {"Message": "Post updated successfully"}


# Delete a post
@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
	index = find_post_index(post_id)
	if index is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
	my_posts.pop(index)
	return Response(status_code=status.HTTP_204_NO_CONTENT)
