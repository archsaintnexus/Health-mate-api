from fastapi import FastAPI
from app.util.init_db import create_tables
from contextlib import asynccontextmanager
from app.routers.auth import authRouter

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB at startup
    print(" ")
    print("Initializing database _tables...")
    create_tables()
    yield # Allow the application to run - Seperation point
    # Cleanup code can be added here if needed

app = FastAPI(lifespan=lifespan)
app.include_router(router=authRouter, tags=["auth"], prefix="/auth") # Include the auth router with the prefix "/auth"


@app.get("/health")
async def health_check():
    return {"Status": "Running...."}



