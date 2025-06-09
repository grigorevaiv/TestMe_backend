from pydantic import BaseModel
from typing import Optional

class InterpretationSchema(BaseModel):
    id: Optional[int] = None
    text: str
    level: int
    scaleId: int

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Interpretation(Base):
    __tablename__ = 'interpretations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    scaleId = Column(Integer, ForeignKey('scales.id'), nullable=False)
    scale = relationship("Scale", back_populates="interpretations")
    scale_results = relationship("ScaleResult", back_populates="interpretation", cascade="all, delete-orphan")
    