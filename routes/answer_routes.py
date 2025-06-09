from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db

from models.answer_model import AnswerSchema
from controllers.answer_controller import (
    batch_create_answers,
    get_all_test_answers,
    batch_update_answers
)

answer_routes = APIRouter()

@answer_routes.post("/answers/batch")
def batchCreateAnswers(answers: list[AnswerSchema], db: Session = Depends(get_db)):
    """
    Batch create answers for a specific test.
    """
    if not answers:
        raise HTTPException(status_code=400, detail="No answers provided for batch creation.")
    
    created_answers = batch_create_answers(answers, db)
    return {"message": "Answers created successfully", "answers": created_answers}

@answer_routes.get("/{test_id}/answers")
def getTestAnswers(test_id: int, db: Session = Depends(get_db)):
    """
    Get all answers for a specific test.
    """
    answers = get_all_test_answers(test_id, db)
    return answers

@answer_routes.put("/answers/batch")
def batchUpdateAnswers(answers: list[AnswerSchema], db: Session = Depends(get_db)):
    """
    Batch update answers for a specific test.
    """
    if not answers:
        raise HTTPException(status_code=400, detail="No answers provided for batch update.")
    
    updated_answers = batch_update_answers(answers, db)
    return {"message": "Answers updated successfully", "answers": updated_answers}