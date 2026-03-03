from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.db.schema.user import UserInCreate, UserInLogin, UserInUpdate, UserWithToken, UserOutput
from fastapi import HTTPException
from app.service.userService import UserService
from sqlalchemy.orm import Session
import logging
from app.util.protectRoute import get_current_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)






authRouter = APIRouter() # The router object

@authRouter.post("/login", status_code=200, response_model=UserWithToken)
async def login(loginDetails: UserInLogin, db: Session = Depends(get_db)):
    try: 
        return UserService(session=db).login(login_details=loginDetails) # This is to call the login method of the UserService class and pass the login details provided by the client and the database session.
    # Implement login logic here
    except Exception as e:
        logger.exception("Error in login")
    raise HTTPException(status_code=500, detail="Internal server error")
    



@authRouter.post("/signup", status_code=201, response_model=UserOutput)
async def signup(signupDetails: UserInCreate, db: Session = Depends(get_db)):
    try:
        return UserService(session=db).signup(user_details=signupDetails) # This is to call the signup method of the UserService class and pass the user details provided by the client and the database session.
    except Exception as e:
        print(f"Error in signup: {str(e)}")

        raise HTTPException(status_code=500, detail=f"Error in signup: {str(e)}")


@authRouter.get("/me", status_code=200, response_model=UserOutput)
async def get_my_details(
    current_user: UserOutput = Depends(get_current_user),
    db: Session = Depends(get_db)
):
     
    try:
        return UserService(session=db).get_me(user_id=current_user.id)
    except Exception as e:
        logger.exception("Error fetching profile")
        raise HTTPException(status_code=500, detail="Internal server error")




@authRouter.put("/me", status_code=200, response_model=UserOutput)
async def update_me(
    update_data: UserInUpdate,
    current_user: UserOutput = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        update_data.id = current_user.id
        return UserService(session=db).update_user(
            user_id=current_user.id,
            update_data=update_data
        )
    except Exception as e:
        logger.exception("Error updating profile")
        raise HTTPException(status_code=500, detail="Internal server error")
    

