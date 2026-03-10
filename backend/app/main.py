from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core import auth
from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.api import tasks, webhooks, auth
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Board API",
    description="B2B Task Board App",
    version="1.0.0"
)


@app.get("/")
def root():
    return {"message": "API is running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)
app.include_router(webhooks.router)
app.include_router(auth.router)


