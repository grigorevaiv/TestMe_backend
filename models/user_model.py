from pydantic import BaseModel, Field
from typing import Optional
from models.state_model import StateSchema

def to_camel(string: str) -> str:
    parts = string.split('_')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])

class UserSchema(BaseModel):
    id: Optional[int] = None
    email: str
    first_name: str
    last_name: str
    birth_date: str | None = None
    is_active: Optional[bool] = True
    assigned_to_admin: Optional[int] = None

    model_config = {
        "from_attributes": True,
        "alias_generator": to_camel,
        "populate_by_name": True
    }

def to_camel(s: str) -> str:
    parts = s.split('_')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birth_date = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    assigned_to_admin = Column(Integer, ForeignKey("admins.id"), nullable=False)
    test_results = relationship("TestResult", back_populates="user")
    scale_results = relationship("ScaleResult", back_populates="user")
    admins = relationship("Admin", back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, first_name={self.first_name}, last_name={self.last_name})>"
    

    from sqlalchemy import Column, Integer, String, Boolean#, Enum
from database.database import Base
