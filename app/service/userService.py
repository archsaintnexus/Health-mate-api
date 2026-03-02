from app.db.repository.userRepo import UserRepository
from app.db.schema.user import UserInCreate, UserInLogin, UserOutput, UserWithToken
from app.core.security.authHandler import AuthHandler
from app.core.security.hashHelper import HashHelper
from sqlalchemy.orm import Session
from fastapi import HTTPException



class UserService:
  def __init__(self, session: Session):
    self.__userRepository = UserRepository(session=session)

  def signup(self, user_details: UserInCreate) -> UserOutput:
    if self.__userRepository.user_exist_by_email(email=user_details.email):
      raise HTTPException(status_code=400, detail="User with this email already exists. Login Instead")
    
    hashed_password = HashHelper.get_password_hash(plain_password=user_details.password) # This is to hash the password before storing it in the database.
    user_details.password = hashed_password # This is to replace the plain password with the hashed password in the user details.
    return self.__userRepository.create_user(user_data=user_details) # This is to create a new user in the database with the user details provided by the client.
  
  def login(self, login_details: UserInLogin) -> UserWithToken:
    if not self.__userRepository.user_exist_by_email(email=login_details.email):
      raise HTTPException(status_code=404, detail="User with this email does not exist. Please signup first.")
    
    user = self.__userRepository.get_user_by_email(email=login_details.email) # This is to get the user from the database using the email provided by the client.
    if HashHelper.verify_password(plain_password=login_details.password, hashed_password=user.password): # This is to verify the password provided by the client with the hashed password stored in the database.
      token = AuthHandler.sign_jwt(user_id=user.id) # This is to create a token for the user using the user id.
      if token: 
        return UserWithToken(token=token) # This is to return the user details along with the token to the client.
      raise HTTPException(status_code=500, detail="Error in generating token. Please try again.")
    
    raise HTTPException(status_code=400, detail="Incorrect password. Please check your credentials.")





