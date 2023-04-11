import time  # To add time pause between connection failing and retry connecting to the database

from fastapi import FastAPI  # The fastAPI
from fastapi import HTTPException, status, Depends, Response  # To raise appropriate HTTP Exception and set http status

from psycopg2.extras import RealDictCursor  # To get the column names when we return something from the database
from pydantic import BaseModel  # To specify a schema of what the post request data should look like
import psycopg2  # Library to deal with our Postgres database

from sqlalchemy.orm import Session
from sqlalchemy import desc

from .database import engine, get_db  # Session from database.py file
from . import models  # Models.py file with all the defined tables

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


# Path Operations

# Create a post
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post, db: Session = Depends(get_db)):  # Get post data from user
	new_post = models.Post(**post.dict())  # Query to add new post to db
	db.add(new_post)  # Run query
	db.commit()  # Commit changes
	db.refresh(new_post)  # Update the var with new post
	return {"Post Created": new_post}  # Return post to the user


# Get all posts
@app.get("/posts", status_code=status.HTTP_200_OK)
def get_all_posts(db: Session = Depends(get_db)):
	posts = db.query(models.Post).all()  # Query to get all the posts
	return {"All Posts": posts}  # Return all posts to the user


# Find the latest post
@app.get("/posts/latest", status_code=status.HTTP_200_OK)
def get_latest_post(db: Session = Depends(get_db)):
	post = db.query(models.Post).order_by(desc(models.Post.created_at)).first()  # Query to get the latest post
	
	if not post:  # If post not found set http status to 404
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No posts yet.")
	return {"Latest Post": post}  # Return the latest post


# Find a specific post using the post id
@app.get("/posts/{post_id}", status_code=status.HTTP_200_OK)
def get_post(post_id: int, db: Session = Depends(get_db)):  # The post id should be int.
	post = db.query(models.Post).filter(models.Post.id == post_id).first()  # Query to get the specific post
	if not post:  # If post not found set http status to 404
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found.")
	return {"Post found": post}  # Return post


# Update Post
@app.put("/posts/{post_id}")
def update_post(post_id: int, post: Post, db: Session = Depends(get_db)):
	post_query = db.query(models.Post).filter(models.Post.id == post_id)  # Query to get the specific post
	old_post = post_query.first()  # The post itself
	
	if old_post is None:  # If post not found set http status to 404
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
	
	post_query.update(post.dict(), synchronize_session=False)  # update the post with user provided info
	db.commit()  # Commit changes
	db.refresh(old_post)  # Refresh the old post
	updated_post = old_post
	return {"Post Updated": updated_post}  # Return the updated post


# Delete a post
@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
	post = db.query(models.Post).filter(models.Post.id == post_id)  # Query to get the specific post
	
	if post.first() is None:  # If post not found set http status to 404
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
	
	post.delete(synchronize_session=False)  # Delete the post
	db.commit()  # Commit changes to the database
	return Response(status_code=status.HTTP_204_NO_CONTENT)  # Return positive response
