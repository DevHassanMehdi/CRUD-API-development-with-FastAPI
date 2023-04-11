from .database import Base
from sqlalchemy import Column, Integer, String, Boolean


# Create our table in the database
class Post(Base):
	__tablename__ = "posts"
	
	id = Column(Integer, primary_key=True, nullable=False)
	title = Column(String, nullable=False)
	content = Column(String, nullable=False)
	published = Column(Boolean, server_default="True", nullable=False)
