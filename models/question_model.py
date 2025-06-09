from pydantic import BaseModel
from typing import Optional

class QuestionSchema(BaseModel):
    id: Optional[int] = None
    text: str
    imageUrl: Optional[str] = None
    isActive: bool = True
    blockId: int

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base
from models.answer_model import Answer

class Question(Base):
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    imageUrl = Column(String, nullable=True)
    isActive = Column(Boolean, default=True)
    blockId = Column(Integer, ForeignKey('blocks.id'), nullable=False)

    block = relationship("Block", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    user_answers = relationship("UserAnswer", back_populates="question", cascade="all, delete-orphan")

