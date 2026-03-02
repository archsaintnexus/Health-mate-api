from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.db.schema.user import UserInCreate, UserInLogin, UserInUpdate, UserWithToken
from fastapi import HTTPException
from app.service.userService import UserService
from sqlalchemy.orm import Session

authRouter = APIRouter() # The router object

@authRouter.post("/login")
async def login(loginDetails: UserInLogin, db: Session = Depends(get_db)):
    try: 
        return UserService(session=db).login(login_details=loginDetails) # This is to call the login method of the UserService class and pass the login details provided by the client and the database session.
    # Implement login logic here
    except Exception as e:
        print(f"Error in login: {str(e)}")

        raise HTTPException(status_code=500, detail=f"Error in login: {str(e)}")
    



@authRouter.post("/signup")
async def signup(userDetails: UserInCreate, db: Session = Depends(get_db)):
    try:
        return UserService(session=db).signup(user_details=userDetails) # This is to call the signup method of the UserService class and pass the user details provided by the client and the database session.
    except Exception as e:
        print(f"Error in signup: {str(e)}")

        raise HTTPException(status_code=500, detail=f"Error in signup: {str(e)}")
    

