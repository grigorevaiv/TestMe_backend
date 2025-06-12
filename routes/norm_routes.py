from typing import List
from fastapi import APIRouter, HTTPException, Depends
from auth.check_admin import get_current_admin
from models.question_model import Question
from sqlalchemy.orm import Session
from database.database import get_db

from models.norm_model import NormSchema
from controllers.norm_controller import (
    batch_create_norms,
    get_test_norms,
    batch_update_norms
)

norm_routes = APIRouter(dependencies=[Depends(get_current_admin)])
@norm_routes.post("/batch/norms")
def create_norms(norms: List[NormSchema], db: Session = Depends(get_db)):
    """
    Create multiple norms.
    """
    if not norms:
        raise HTTPException(status_code=400, detail="No norms provided")
    created_norms = batch_create_norms(norms, db)
    return created_norms

@norm_routes.put("/batch/norms")
def update_norms(norms: List[NormSchema], db: Session = Depends(get_db)):
    """
    Update multiple norms.
    """
    if not norms:
        raise HTTPException(status_code=400, detail="No norms provided")
    updated_norms = batch_update_norms(norms, db)
    return updated_norms

@norm_routes.get("/{test_id}/norms")
def getTestNorms(test_id: int, db: Session = Depends(get_db)):
    """
    Get all norms for a specific test.
    """
    norms = get_test_norms(test_id, db)
    return norms



@norm_routes.get("/all-questions")
def get_all_questions(db: Session = Depends(get_db)):
    questions = db.query(Question).all()
    return questions
