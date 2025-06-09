from pydantic import BaseModel
from typing import Optional

class BlockSchema(BaseModel):
    name: str
    order: Optional[int] = None
    instructions: str
    hasTimeLimit: Optional[bool] = None
    timeLimit: Optional[int] = None
    randomizeQuestions: Optional[bool] = None
    randomizeAnswers: Optional[bool] = None
    numberOfQuestions: int
    questionsType: str
    numberOfAnswers: int
    testId: int

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Block(Base):
    __tablename__ = 'blocks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    instructions = Column(String, nullable=False)
    hasTimeLimit = Column(Boolean, default=False)
    timeLimit = Column(Integer, default=0)
    randomizeQuestions = Column(Boolean, default=False)
    randomizeAnswers = Column(Boolean, default=False)
    numberOfQuestions = Column(Integer, default=5, nullable=False)
    questionsType = Column(String, nullable=False)
    numberOfAnswers = Column(Integer, nullable=False)
    testId = Column(Integer, ForeignKey('tests.id'), nullable=False)
    test = relationship("Test", back_populates="blocks")
    scales = relationship("Scale", back_populates="block")
    questions = relationship("Question", back_populates="block")