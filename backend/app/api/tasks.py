

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import jwt
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.auth import AuthUser, require_view, require_create, require_edit, require_delete
from backend.app.models.task import Task
from backend.app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/tasks/login")

@router.get("/")
async def list_tasks(token: str = Depends(oauth2_scheme)):
    return {"message": "Authorized", "token": token}

# ====================== LOGIN (for testing) ======================
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Simple login for testing - replace with real user check later"""
    if form_data.username != "test" or form_data.password != "12345":
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {
        "sub": "test_user_id",
        "org_id": "test_org_id",
        "org_permissions": ["org:tasks:view", "org:tasks:create", "org:tasks:edit", "org:tasks:delete"],
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    access_token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")
    return {"access_token": access_token, "token_type": "bearer"}


# ====================== REAL CRUD ENDPOINTS ======================
@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    user: AuthUser = Depends(require_view), 
    db: Session = Depends(get_db)
):
    tasks = db.query(Task).filter(Task.org_id == user.org_id).all()
    return tasks


@router.post("/", response_model=TaskResponse)
def create_task(
    task_data: TaskCreate,
    user: AuthUser = Depends(require_create),
    db: Session = Depends(get_db)
):
    task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        org_id=user.org_id,
        created_by=user.user_id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, user: AuthUser = Depends(require_view), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.org_id == user.org_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    task_data: TaskUpdate,
    user: AuthUser = Depends(require_edit),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id, Task.org_id == user.org_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task_data.title is not None: task.title = task_data.title
    if task_data.description is not None: task.description = task_data.description
    if task_data.status is not None: task.status = task_data.status
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, user: AuthUser = Depends(require_delete), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.org_id == user.org_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return None



