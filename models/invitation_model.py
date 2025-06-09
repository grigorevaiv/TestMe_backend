from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Optional
from models.state_model import StateSchema

def to_camel(string: str) -> str:
    parts = string.split('_')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])

class CreateInvitationSchema(BaseModel):
    user_email: str
    user_id: int
    test_id: int
    
    model_config = {
        "from_attributes": True,
        "alias_generator": to_camel,
        "populate_by_name": True
    }

class InvitationSchema(BaseModel):
    id: Optional[int] = None
    token: str
    user_id: int
    test_id: int
    expires_at: datetime
    used: bool = False

    model_config = {
        "from_attributes": True,
        "alias_generator": to_camel,
        "populate_by_name": True
    }

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database.database import Base
class Invitation(Base):
    __tablename__ = 'invitations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, nullable=False, unique=True)
    user_id = Column(Integer, nullable=False)
    test_id = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Invitation(id={self.id}, token={self.token}, user_id={self.user_id}, test_id={self.test_id})>"