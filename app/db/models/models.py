from app.core.database import Base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime




class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False) # The "String(50)" allows to restrict the length of the first name to 50 characters.
    last_name = Column(String(100), nullable=False) 
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String(250), nullable=False) # Restriction is set to 250 characters to accommodate hashed passwords, which can be longer than plain text passwords.
    created_at = Column(DateTime, default=datetime.utcnow)