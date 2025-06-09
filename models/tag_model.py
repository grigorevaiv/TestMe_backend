from pydantic import BaseModel
from typing import Optional

class TagSchema(BaseModel):
    id: Optional[int] = None
    name: str

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    tag_tests = relationship("TagTest", back_populates="tag")

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"