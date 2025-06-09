from pydantic import BaseModel, Field
from typing import Optional

class TagTestSchema(BaseModel):
    id: Optional[int] = None
    tag_id: int = Field(..., alias="tagId")
    test_id: int = Field(..., alias="testId")

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class TagTest(Base):
    __tablename__ = 'tag_tests'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)

    tag = relationship("Tag", back_populates="tag_tests")
    test = relationship("Test", back_populates="tag_tests")

    def __repr__(self):
        return f"<TagTest(id={self.id}, tag_id={self.tag_id}, test_id={self.test_id})>"
