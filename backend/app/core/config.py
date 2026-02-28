import os
from dotenv import load_dotenv


# Load .env from the backend folder (works no matter where you run uvicorn)
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')

if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    print(f"DEBUG: .env loaded from: {env_path}")
else:
    print(f"ERROR: .env not found at {env_path}")


class Config:
    CLERK_SECRET_KEY: str = os.getenv("CLERK_SECRET_KEY", "")
    CLERK_PUBLISHABLE_KEY: str = os.getenv("CLERK_PUBLISHABLE_KEY", "")
    CLERK_WEBHOOK_SECRET: str = os.getenv("CLERK_WEBHOOK_SECRET", "")
    CLERK_JWKS_URL: str = os.getenv("CLERK_JWKS_URL", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "")
    FREE_TIER_LIMIT: int = 2
    PRO_TIER_MEMBERSHIP_LIMIT = 0  # unlimited

    def __init__(self):
        print(f"DEBUG: DATABASE_URL = {self.DATABASE_URL}")
        print(f"DEBUG: All env vars example: CLERK_SECRET_KEY = {self.CLERK_SECRET_KEY}")
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is not set. Add it to .env like 'mysql+pymysql://user:pass@host:port/db'")


# ←←← This must stay at the very bottom
settings = Config()








