from pydantic import BaseModel
from typing import Optional

class AnswerSchema(BaseModel):
    id: Optional[int] = None
    text: str
    questionId: int

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Answer(Base):
    __tablename__ = 'answers'
    
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    questionId = Column(Integer, ForeignKey('questions.id', ondelete="CASCADE"), nullable=False)
    

    question = relationship("Question", back_populates="answers")
    weights = relationship("Weight", back_populates="answer", cascade="all, delete-orphan")
    user_answers = relationship("UserAnswer", back_populates="answer", cascade="all, delete-orphan")