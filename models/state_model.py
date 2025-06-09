from pydantic import BaseModel
from typing import Optional

class StateSchema(BaseModel):
    testId: int
    state: str
    currentStep: int


from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base

class State(Base):
    __tablename__ = 'states'
    id = Column(Integer, primary_key=True, autoincrement=True)
    testId = Column(Integer, ForeignKey('tests.id'), nullable=False)
    state = Column(String, nullable=False)
    currentStep = Column(Integer, nullable=False)
    test = relationship("Test", back_populates="state")

