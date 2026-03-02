import jwt
from decouple import config
import time

JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITHM = config("JWT_ALGORITHM") 



class AuthHandler(object):
  @staticmethod
  def sign_jwt(user_id: int) -> str:
    payload = {
      "user_id": user_id,
      "expires": time.time() + 900 # This is to set the expiration time of the token, which is 15 minutes in this case.
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token # this creates a token for the user, which is a string that contains the payload and the signature.
  
  @staticmethod
  def decode_jwt(token: str) -> dict:
    try:
      decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
      return decoded_token if decoded_token["expires"] >= time.time() else None # This is to check if the token is expired or not. If the token is expired, it returns None.
    except:
      print("Unable to decode the token. Invalid token.")
      return {} # This is to handle the case when the token is invalid. It returns an empty dictionary.



