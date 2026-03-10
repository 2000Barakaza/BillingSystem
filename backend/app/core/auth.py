import httpx
from fastapi import Depends, HTTPException, Request, status
from clerk_backend_api.security import AuthenticateRequestOptions
from fastapi.security import OAuth2PasswordBearer
from backend.app.core.config import settings
from backend.app.core.clerk import clerk
from jose import jwt, JWTError  # Add pyjwt


# ====================== CENTRAL SECURITY SCHEME ======================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")   # ← CORRECT URL


class AuthUser:
    def __init__(self, user_id: str, org_id: str, org_permissions: list):
        self.user_id = user_id
        self.org_id = org_id
        self.org_permissions = org_permissions

    def has_permission(self, permission: str) -> bool:
        return permission in self.org_permissions

    @property
    def can_view(self) -> bool:
        return self.has_permission("org:tasks:view")

    @property
    def can_create(self) -> bool:
        return self.has_permission("org:tasks:create")

    @property
    def can_delete(self) -> bool:
        return self.has_permission("org:tasks:delete")

    @property
    def can_edit(self) -> bool:
        return self.has_permission("org:tasks:edit")

def convert_to_httpx_request(fastapi_request: Request) -> httpx.Request:
    return httpx.Request(
        method=fastapi_request.method,
        url=str(fastapi_request.url),
        headers=dict(fastapi_request.headers)
    )

async def get_current_user(request: Request) -> AuthUser:
    # Pata token kutoka headers (Bearer scheme)
    authorization: str = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = authorization.split(" ")[1]

    # Dev mode bypass: Verify simple JWT badala ya Clerk
    if settings.DEBUG:
        try:
            claims = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = claims.get("sub")
            org_id = claims.get("org_id")
            org_permissions = claims.get("org_permissions", [])
            if user_id and org_id:
                return AuthUser(user_id=user_id, org_id=org_id, org_permissions=org_permissions)
        except JWTError:
            pass  # Enda kwa Clerk kama fail

    # Normal Clerk verification
    httpx_request = convert_to_httpx_request(request)
    request_state = clerk.authenticate_request(
        httpx_request,
        AuthenticateRequestOptions(authorized_parties=[settings.FRONTEND_URL])
    )
    if not request_state.is_signed_in:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    claims = request_state.payload
    user_id = claims.get("sub")
    org_id = claims.get("org_id")
    org_permissions = claims.get("org_permissions", [])  # Updated kutoka "permissions" au fallback []

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No organization selected")

    return AuthUser(user_id=user_id, org_id=org_id, org_permissions=org_permissions)

def require_view(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if not user.can_view:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="View permission required")
    return user

def require_create(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if not user.can_create:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Create permission required")
    return user

def require_delete(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if not user.can_delete:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Delete permission required")
    return user

def require_edit(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if not user.can_edit:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Edit permission required")
    return user




from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from backend.app.core.config import settings

# ==================== CORRECT TOKEN URL ====================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class AuthUser:
    def __init__(self, user_id: str, org_id: str, org_permissions: list):
        self.user_id = user_id
        self.org_id = org_id
        self.org_permissions = org_permissions

    def has_permission(self, permission: str) -> bool:
        return permission in self.org_permissions

    @property
    def can_view(self): return self.has_permission("org:tasks:view")
    @property
    def can_create(self): return self.has_permission("org:tasks:create")
    @property
    def can_edit(self): return self.has_permission("org:tasks:edit")
    @property
    def can_delete(self): return self.has_permission("org:tasks:delete")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> AuthUser:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return AuthUser(
            user_id=payload.get("sub"),
            org_id=payload.get("org_id"),
            org_permissions=payload.get("org_permissions", [])
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    




    


    