import time  # To add time pause between connection failing and retry connecting to the database

import psycopg2  # Library to deal with our Postgres database
from fastapi import FastAPI  # The fastAPI
from fastapi import HTTPException, status  # To raise appropriate HTTP Exception and set http status
from psycopg2.extras import RealDictCursor  # To get the column names when we return something from the database
from pydantic import BaseModel  # To specify a schema of what the post request data should look like

from . import models  # Models.py file with all the defined tables
from .database import engine  # Session from database.py file

# To create all the defined models. These models are the tables we defined in the models.py file.
models.Base.metadata.create_all(bind=engine)

# Initialize our app
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
	cursor.execute(
		"""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
		(post.title, post.content, post.published))
	new_post = cursor.fetchone()
	connection.commit()
	return {"Post Created": new_post}


# Get all posts
@app.get("/posts", status_code=status.HTTP_200_OK)
def get_all_posts():
	cursor.execute("""SELECT * FROM posts""")
	posts = cursor.fetchall()
	return {"All Posts": posts}


# Find the latest post
@app.get("/posts/latest", status_code=status.HTTP_200_OK)
def get_latest_post():
	cursor.execute("""SELECT * FROM posts ORDER BY id DESC LIMIT 1""")
	post = cursor.fetchone()
	if not post:  # If item not found set http status to 404
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No posts yet.")
	return {"Latest Post": post}


# Find a specific post using the post id
@app.get("/posts/{post_id}", status_code=status.HTTP_200_OK)
def get_post(post_id: int):  # The post id should be int.
	cursor.execute("""SELECT * FROM posts WHERE id = %s""", str(post_id))
	post = cursor.fetchone()
	if not post:  # If item not found set http status to 404
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found.")
	return {"Post found": post}


# Update Post
@app.put("/posts/{post_id}")
def update_post(post_id: int, post: Post):
	cursor.execute(
		"""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
		(post.title, post.content, post.published, str(post_id)))
	updated_post = cursor.fetchone()
	connection.commit()
	if updated_post is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
	return {"Post Updated": updated_post}


# Delete a post
@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
	cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", str(post_id))
	post = cursor.fetchone()
	connection.commit()
	if post is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
	return {"Post Deleted": post}
