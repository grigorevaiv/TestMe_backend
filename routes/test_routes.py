from typing import List
from fastapi import Request
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from auth.check_admin import get_current_admin
from database.database import get_db
from models.admin_model import Admin
from models.question_model import Question
from models.test_model import Test, TestSchema
from models.block_model import Block, BlockSchema
from models.scale_model import ScaleSchema
from models.state_model import StateSchema, State

from controllers.test_controller import (
    create_test,
    get_test,
    get_all_tests,
    update_test,
)

test_routes = APIRouter(dependencies=[Depends(get_current_admin)])

@test_routes.post("")
def createTest(test: TestSchema, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    return create_test(test, db, current_admin)

@test_routes.get("")
def getTests(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    return get_all_tests(db, current_admin)

@test_routes.get("/{test_id}")
def getTestById(test_id: int, db: Session = Depends(get_db)):
    return get_test(test_id, db)

@test_routes.put("/{test_id}")
def updateTest(test_id: int, test: TestSchema, db: Session = Depends(get_db)):
    return update_test(test_id, test, db)

@test_routes.patch("/{test_id}/deactivate")
def deactivateTest(test_id: int, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    state = db.query(State).filter(Test.id == State.testId).first()
    state.state = "inactive"
    db.commit()
    return {"message": "Test deactivated successfully"}

@test_routes.patch("/{test_id}/reactivate")
def reactivateTest(test_id: int, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    state = db.query(State).filter(State.testId == test_id).first()
    if state.currentStep == 8:
        state.state = "active"
    else:
        state.state = "draft"
    db.commit()
    return {"message": "Test reactivated successfully"}