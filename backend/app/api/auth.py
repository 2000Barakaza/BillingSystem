


from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from jose import jwt
from datetime import datetime, timedelta
from backend.app.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


# === FIXED: Correct tokenUrl pointing to this exact login endpoint ===
#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "test" or form_data.password != "12345":
        return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})

    token_data = {
        "sub": "test_user_id",
        "org_id": "test_org_id",
        "org_permissions": ["org:tasks:view", "org:tasks:create", "org:tasks:edit", "org:tasks:delete"],
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    access_token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")
    return {"access_token": access_token, "token_type": "bearer"}





