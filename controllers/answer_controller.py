from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.answer_model import Answer, AnswerSchema
from models.block_model import Block
from models.question_model import Question

def batch_create_answers(answers: List[AnswerSchema], db: Session):
    created = []

    for answer in answers:
        new_answer = Answer(
            text=answer.text,
            questionId=answer.questionId
        )
        db.add(new_answer)
        created.append(new_answer)

    db.commit()
    for item in created:
        db.refresh(item)

    return created

def get_all_test_answers(test_id: int, db: Session):
    answers = (
        db.query(Answer)
        .join(Answer.question)
        .join(Question.block)
        .filter(Block.testId == test_id)
        .order_by(Answer.id)
        .all()
    )
    if not answers:
        raise HTTPException(status_code=404, detail="No answers found for this test.")
    return answers

def batch_update_answers(answers: List[AnswerSchema], db: Session):
    updated = []

    for answer in answers:
        existing_answer = db.query(Answer).filter(Answer.id == answer.id).first()
        if not existing_answer:
            raise HTTPException(status_code=404, detail=f"Answer with id {answer.id} not found.")
        
        existing_answer.text = answer.text
        db.add(existing_answer)
        updated.append(existing_answer)

    db.commit()
    for item in updated:
        db.refresh(item)

    return updated