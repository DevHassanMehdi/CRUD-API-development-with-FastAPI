from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQL Alchemy connection URL
SQLALCHEMY_DATABASE_URL = 'postgres://postgres:root@localhost/fastapi'

# SQL Alchemy connection engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session to talk to the database
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class used to create models
Base = declarative_base()
