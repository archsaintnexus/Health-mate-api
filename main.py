from fastapi import FastAPI, Depends
from app.util.init_db import create_tables
from contextlib import asynccontextmanager
from app.routers.auth import authRouter
from app.util.protectRoute import get_current_user
from app.db.schema.user import UserOutput
from fastapi.middleware.cors import CORSMiddleware
from app.routers.appointment import appointmentRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB at startup
    print("\nInitializing database _tables...")
    create_tables()
    yield # Allow the application to run - Seperation point
    # Cleanup code can be added here if needed

app = FastAPI(lifespan=lifespan)
app.include_router(router=authRouter, tags=["auth"], prefix="/auth") # Include the auth router with the prefix "/auth"
app.include_router(appointmentRouter, prefix="/appointments", tags=["appointments"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)






@app.get("/health")
async def health_check():
    return {"Status": "Running...."}



@app.get("/protected")
def read_protected(user: UserOutput = Depends(get_current_user)):
    return {"data": user}

