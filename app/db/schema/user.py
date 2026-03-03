from pydantic import EmailStr, BaseModel
from typing import Union



# Creating users schemas for request and response
class UserInCreate(BaseModel):
  first_name: str
  last_name: str
  email: EmailStr # To restrict the email.
  password: str


# This is what we send back to the client after creating a user.
class UserOutput(BaseModel):
  id: int
  first_name: str
  last_name: str
  email: EmailStr


# What we expect from user when they want to update the properties of their account.

class UserInUpdate(BaseModel):
  id: int
  first_name: Union[str, None] = None # This means that the first name can be either a string or None (if the user doesn't want to update it).
  last_name: Union[str, None] = None # This makes it optional for the user to update their last name.
  email: Union[EmailStr, None] = None
  password: Union[str, None] = None


# If the user wants to login.
class UserInLogin(BaseModel):
  email: EmailStr
  password: str


# Token given to user with the output.
class UserWithToken(BaseModel):
  token: str



