from pydantic import BaseModel
from typing import Optional

class NormSchema(BaseModel):
    id: Optional[int] = None
    scaleId: int
    mean: float
    stdDev: float
    type: str

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from database.database import Base

class Norm(Base):
    __tablename__= 'norms'
    id = Column(Integer, primary_key=True, autoincrement=True)
    scaleId = Column(Integer, ForeignKey('scales.id'), nullable=False)
    mean = Column(Float, nullable=False)
    stdDev = Column(Float, nullable=False)
    type = Column(String, nullable=False)
    scale = relationship("Scale", back_populates="norms")