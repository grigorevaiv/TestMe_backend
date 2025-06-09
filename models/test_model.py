from pydantic import BaseModel
from typing import List, Optional

class TestSchema(BaseModel):
    title: str
    author: Optional[str] = None
    version: Optional[str] = None
    description: str
    instructions: str
    tags: Optional[List[str]] = []

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base

class Test(Base):
    __tablename__ = 'tests'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=True)
    version = Column(String, nullable=True)
    description = Column(String, nullable=False)
    instructions = Column(String, nullable=False)
    blocks = relationship("Block", back_populates="test", cascade="all, delete-orphan")
    state = relationship("State", back_populates="test", uselist=False, cascade="all, delete-orphan")
    scales = relationship("Scale", back_populates="test", cascade="all, delete-orphan")
    tag_tests = relationship("TagTest", back_populates="test", cascade="all, delete-orphan")
    test_results = relationship("TestResult", back_populates="test")
    scale_results = relationship("ScaleResult", back_populates="test")



