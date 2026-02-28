

#import uuid
#from datetime import datetime
#from sqlalchemy import Column, String, Text, DateTime, Enum
#import enum
#from backend.app.core.database import Base

#class TaskStatus(str, enum.Enum):
#    PENDING = "pending"
#    STARTED = "started"
#    COMPLETED = "completed"

#class Task(Base):
#    __tablename__ = "tasks"
#    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
#    title = Column(String(255), nullable=False)
#    description = Column(Text, nullable=True)
#    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
#    org_id = Column(String, nullable=False, index=True)
#    created_by = Column(String, nullable=False)
#    created_at = Column(DateTime, default=datetime.utcnow)
#    updated_at = Column(DateTime, default=datetime.utcnow)



import uuid
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.orm import declarative_base  # or however you import Base
from backend.app.core.database import Base   # ← your Base

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default=TaskStatus.TODO.value, index=True)
    priority = Column(String(20), default="medium")
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Task {self.title}>"

__all__ = ["Task", "TaskStatus"]





