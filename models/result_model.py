from typing import Dict, List
from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from database.database import Base
from pydantic import BaseModel

class UserAnswerSchema(BaseModel):
    userId: int
    answers: Dict[int, List[int]]

    class Config:
        orm_mode = True

class UserAnswer(Base):
    __tablename__ = 'user_answers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    testResultId = Column(Integer, ForeignKey('test_result.id'), nullable=False)
    answerId = Column(Integer, ForeignKey('answers.id'), nullable=False)
    questionId = Column(Integer, ForeignKey('questions.id'), nullable=False)
    test_result = relationship("TestResult", back_populates="user_answers")
    answer = relationship("Answer", back_populates="user_answers")
    question = relationship("Question", back_populates="user_answers")


class TestResultSchema(BaseModel):
    testId: int
    userId: int
    user_answers: List[UserAnswerSchema] = []

    class Config:
        orm_mode = True

class TestResult(Base):
    __tablename__ = 'test_result'
    id = Column(Integer, primary_key=True, autoincrement=True)
    testId = Column(Integer, ForeignKey('tests.id'), nullable=False)
    userId = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="test_results")
    test = relationship("Test", back_populates="test_results")
    user_answers = relationship("UserAnswer", back_populates="test_result")
    scale_results = relationship("ScaleResult", back_populates="test_result")


class ScaleResultSchema(BaseModel):
    testResultId: int
    testId: int
    scaleId: int
    raw: int
    userId: int
    normalized: int | None = None
    interpretationId: int | None = None

    class Config:
        orm_mode = True


class ScaleResult(Base):
    __tablename__ = 'scale_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    testResultId = Column(Integer, ForeignKey('test_result.id'), nullable=False)
    testId = Column(Integer, ForeignKey('tests.id'), nullable=False)  # ← добавлено
    scaleId = Column(Integer, ForeignKey('scales.id'), nullable=False)
    userId = Column(Integer, ForeignKey('users.id'), nullable=False)
    normalized = Column(Integer, nullable=True)
    interpretationId = Column(Integer, ForeignKey('interpretations.id'), nullable=True)

    test_result = relationship("TestResult", back_populates="scale_results")
    scale = relationship("Scale", back_populates="scale_results")
    interpretation = relationship("Interpretation", back_populates="scale_results")
    user = relationship("User", back_populates="scale_results")
    test = relationship("Test", back_populates="scale_results")



