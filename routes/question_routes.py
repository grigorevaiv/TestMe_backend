from fastapi import APIRouter, Depends, Request, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from auth.check_admin import get_current_admin
from database.database import get_db
from models.question_model import Question, QuestionSchema
from controllers.question_controller import (
    get_all_questions,
    upload_temp_image,
    create_questions,
    update_questions,
    delete_image,
    get_questions_by_test
)

question_routes = APIRouter(dependencies=[Depends(get_current_admin)])


@question_routes.get("/questions/all")
def get_all_questions_route(db: Session = Depends(get_db)):
    """
    Retrieve all questions from the database.
    """
    try:
        return get_all_questions(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@question_routes.post("/upload-temp-image")
def upload_temp_image_route(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    test_id: int = Form(...)
):
    """
    Upload a temporary image for a question, tied to a specific test.
    """
    try:
        return upload_temp_image(db, file, test_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@question_routes.post("/{test_id}/questions/batch")
def create_questions_route(
    test_id: int,
    questions: List[QuestionSchema],
    db: Session = Depends(get_db)
):
    """
    Create multiple questions for a test.
    """
    try:
        return create_questions(test_id, questions, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@question_routes.put("/{test_id}/questions/batch")
def update_questions_route(
    test_id: int,
    questions: List[QuestionSchema],
    db: Session = Depends(get_db)
):
    """
    Update multiple questions for a test.
    """
    try:
        return update_questions(test_id, questions, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class DeleteImagePayload(BaseModel):
    imageUrl: str

@question_routes.delete("/delete-image")
def delete_image_route(
    payload: DeleteImagePayload,
    db: Session = Depends(get_db)
):
    """
    Delete a question's image and clear its reference in the database.
    """
    try:
        return delete_image(payload, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@question_routes.get("/{test_id}/questions")
def get_questions_by_test_id_route(test_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all questions for a specific test, grouped by blocks.
    """
    try:
        return get_questions_by_test(test_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class QuestionDeleteRequest(BaseModel):
    ids: List[int]

@question_routes.delete("/questions/batch/")
def delete_questions_batch(payload: QuestionDeleteRequest, db: Session = Depends(get_db)):
    if not payload.ids:
        raise HTTPException(status_code=400, detail="No IDs provided")

    for q_id in payload.ids:
        db.query(Question).filter(Question.id == q_id).delete()
    db.commit()

    return {"status": "ok"}