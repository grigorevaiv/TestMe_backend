from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from models.answer_model import Answer
from models.block_model import Block
from models.question_model import Question
from models.weight_model import Weight, WeightSchema

def create_weights(db: Session, weights: list[WeightSchema]):
    for item in weights:
        db.add(Weight(**item.dict(by_alias=False)))
    db.commit()

def update_weights(db: Session, weights: list[WeightSchema]):
    for item in weights:
        db_item = db.query(Weight).filter(Weight.id == item.id).first()
        if db_item:
            db_item.answerId = item.answerId  
            db_item.scaleId = item.scaleId   
            db_item.value = item.value
    db.commit()

def get_all_weights(test_id: int, db: Session):
    weights = (
        db.query(Weight)
        .join(Weight.answer)
        .join(Answer.question)
        .join(Question.block)
        .filter(Block.testId == test_id)
        .options(joinedload(Weight.answer))
        .order_by(Weight.id)
        .all()
    )
    
    if not weights:
        raise HTTPException(status_code=404, detail="No weights found for this test.")
    
    return weights