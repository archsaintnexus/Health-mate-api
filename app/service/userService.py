from app.db.repository.userRepo import UserRepository
from app.db.schema.user import UserInCreate, UserInLogin, UserOutput, UserWithToken, UserInUpdate
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

  def get_user_by_id(self, user_id: int):
    user = self.__userRepository.get_user_by_id(user_id=user_id)
    if user:
      return user

    raise HTTPException(status_code=400, detail="User is not available")


  def update_user(self, user_id: int, update_data: UserInUpdate) -> UserOutput:
    if update_data.password:
      update_data.password= HashHelper.get_password_hash(update_data.password) # This allows us to hash the password after updated

    user = self.__userRepository.update_user(user_id=user_id, update_data=update_data)

    if not user:
      raise HTTPException(status_code=404, detail="User not found")
    
    return UserOutput(
      id=user.id,
      first_name=user.first_name,
      last_name=user.last_name,
      email=user.email
    )
  
  def get_me(self, user_id: int) -> UserOutput:
    user = self.__userRepository.get_user_by_id(user_id=user_id)
    if not user:
      raise HTTPException(status_code=404, detail="User not found")
    return UserOutput(
      id=user.id,
      first_name=user.first_name,
      last_name=user.last_name,
      email=user.email
    )


