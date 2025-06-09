from typing import List
from fastapi import Request
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.database import get_db
from models.question_model import Question
from models.test_model import Test, TestSchema
from models.block_model import Block, BlockSchema
from models.scale_model import ScaleSchema
from models.state_model import StateSchema

from controllers.test_controller import (
    create_test,
    get_test,
    get_all_tests,
    update_test,
)

test_routes = APIRouter()

@test_routes.post("")
def createTest(test: TestSchema, db: Session = Depends(get_db)):
    return create_test(test, db)

@test_routes.get("")
def getTests(db: Session = Depends(get_db)):
    return get_all_tests(db)

@test_routes.get("/{test_id}")
def getTestById(test_id: int, db: Session = Depends(get_db)):
    return get_test(test_id, db)

@test_routes.put("/{test_id}")
def updateTest(test_id: int, test: TestSchema, db: Session = Depends(get_db)):
    return update_test(test_id, test, db)
