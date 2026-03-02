from .base import BaseRepository
from app.db.models.models import User
from app.db.schema.user import UserInCreate


class UserRepository(BaseRepository): # To store user.
  def create_user(self, user_data: UserInCreate):
    new_user = User(user_data.model_dump(exclude_none=True)) # This ensures no None Values available.

    self.session.add(instance=new_user) # this is to add user to DB
    self.session.commit() # this is to save the changes to DB 
    self.session.refresh(instance=new_user) # this is to refresh the instance of the user, so that we can get the id of the user

    return new_user
  
  def user_exist_by_email(self, email:str) -> bool:
    user = self.session.query(User).filter_by(email=email).first()

    return bool(user)
  
  def get_user_by_email(self, email:str) -> User:
    user = self.session.query(User).filter_by(email=email).first()

    return user
  
  def get_user_by_id(self, user_id: int):
    user = self.session.query(User).filter_by(id=user_id).first()

    return user 

