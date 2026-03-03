from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

database_url=os.getenv("DATABASE_URL") # This gets the db url
engine = create_engine(database_url) # engine creates the factory connection on how python interacts with the db.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # The 'sessionmaker' ensures the db does not auto commit pending operations or incomplete ops.

Base=declarative_base()

def get_db():
  db = SessionLocal() # This allows db session.
  try:
    yield db
  finally:
    db.close


