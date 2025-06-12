from pydantic import BaseModel
from typing import Optional

def to_camel(string: str) -> str:
    parts = string.split('_')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])

class AdminSchema(BaseModel):
    id: Optional[int] = None
    first_name: str
    last_name: str
    email: str
    password: str

    model_config = {
        "from_attributes": True,
        "alias_generator": to_camel,
        "populate_by_name": True
    }

from pydantic import BaseModel

class AdminLoginSchema(BaseModel):
    email: str
    password: str
    
    model_config = {
        "from_attributes": True,
        "alias_generator": to_camel,
        "populate_by_name": True
    }

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base

class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    tests = relationship("Test", back_populates="admin")
    users = relationship("User", back_populates="admins")
