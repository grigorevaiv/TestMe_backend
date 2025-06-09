from pydantic import BaseModel, Field
from typing import Optional

class WeightSchema(BaseModel):
    id: Optional[int] = None
    answerId: int = Field(..., alias="answerId")
    scaleId: int = Field(..., alias="scaleId")
    value: int

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Weight(Base):
    __tablename__ = "weights"

    id = Column(Integer, primary_key=True, index=True)
    answerId = Column(Integer, ForeignKey("answers.id", ondelete="CASCADE"), nullable=False)
    scaleId = Column(Integer, ForeignKey("scales.id", ondelete="CASCADE"), nullable=False)
    value = Column(Integer, nullable=False)

    # relationships (если хочешь удобно джоинить)
    answer = relationship("Answer", back_populates="weights")
    scale = relationship("Scale", back_populates="weights")