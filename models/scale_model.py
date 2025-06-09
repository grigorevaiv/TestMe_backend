from pydantic import BaseModel
from typing import Optional

class ScaleSchema(BaseModel):
    pole1: str
    pole2: Optional[str] = None
    testId: int
    blockId: int
    scaleType: str

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base
class Scale(Base):
    __tablename__ = 'scales'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pole1 = Column(String, nullable=False)
    pole2 = Column(String, nullable=True)
    scaleType = Column(String, nullable=False)
    testId = Column(Integer, ForeignKey('tests.id'), nullable=False)
    blockId = Column(Integer, ForeignKey('blocks.id'), nullable=False)
    test = relationship("Test", back_populates="scales")
    block = relationship("Block", back_populates="scales")
    weights = relationship("Weight", back_populates="scale", cascade="all, delete-orphan")
    norms = relationship("Norm", back_populates="scale", cascade="all, delete-orphan")
    interpretations = relationship("Interpretation", back_populates="scale", cascade="all, delete-orphan")
    scale_results = relationship("ScaleResult", back_populates="scale", cascade="all, delete-orphan")
