from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, Union
from core.security.authHandler import AuthHandler
from service.userService import UserService
from core.database import get_db
from db.schema.user import UserOutput
from db.repository.userRepo import UserRepository
# I CAN'T REMEMBER ALL THIS IMPORT LOL!



AUTH_PREFIX = 'Bearer '
# THIS IS FOR LOCAL PROJECT SETUP
def get_current_user(
     session: Session = Depends(get_db), 
     authorization: Annotated[Union[str, None], Header()] = None
                      ) -> UserOutput:
 
   auth_exception = HTTPException(
     status_code=status.HTTP_401_UNAUTHORIZED, 
     detail="Invalid Authentication Credentials"
   )
   if not authorization: # Raising this auth exception if "authorization" is none.
     raise auth_exception
  
   if not authorization.startswith(AUTH_PREFIX): # If it doesn't start with "Bearer " raise the auth_exception.
     raise auth_exception
  
   payload = AuthHandler.decode_jwt(token=authorization[len(AUTH_PREFIX):])

   if payload and payload["user_id"]:
     try:
       user = UserService(session=session).get_user_by_id(payload["user_id"])
       return UserOutput(
         id = user.id,
         first_name=user.first_name,
         last_name=user.last_name,
         email = user.email
       )
     except Exception as error:
       raise error


   raise auth_exception




# from app.core.security.firebaseAuth import verify_firebase_token

# def get_current_user(
#     session: Session = Depends(get_db),
#     authorization: Annotated[Union[str, None], Header()] = None
# ) -> UserOutput:

#     auth_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Invalid Authentication Credentials"
#     )

#     if not authorization:
#         raise auth_exception

#     if not authorization.startswith("Bearer "):
#         raise auth_exception

#     token = authorization[len("Bearer "):]
    
#     decoded = verify_firebase_token(token)
#     if not decoded:
#         raise auth_exception

#     # Use Firebase UID or email to find the user in your database
#     email = decoded.get("email")
#     user = session.query(User).filter_by(email=email).first()
    
#     if not user:
#         raise auth_exception

#     return UserOutput(
#         id=user.id,
#         first_name=user.first_name,
#         last_name=user.last_name,
#         email=user.email,
#         phone_number=user.phone_number,
#         address=user.address
#     )

