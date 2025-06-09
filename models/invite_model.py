from pydantic import BaseModel, Field
from typing import Optional
from models.state_model import StateSchema
from datetime import datetime

class IncomingInfoSchema(BaseModel):
    email: str
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    admin_id: int = Field(..., alias="adminId")

class IncomingConfirmationSchema(BaseModel):
    token: str
    password: str

class InviteSchema(BaseModel):
    email: str
    first_name: str
    last_name: str
    token: str
    expires_at: datetime
    confirmed: bool = False
    created_by_admin_id: int

class ConfirmInviteSchema(BaseModel):
    token: str
    password: str

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base

class Invite(Base):
    __tablename__ = 'invites'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    token = Column(String, nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    confirmed = Column(Boolean, default=False)
    created_by_admin_id = Column(Integer, nullable=False)