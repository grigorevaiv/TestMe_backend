from typing import List
from fastapi import HTTPException
from models.scale_model import Scale
from sqlalchemy.orm import Session

from models.interpretation_model import Interpretation, InterpretationSchema

def get_test_interpretations(test_id: int, db: Session):
    interpretations = db.query(Interpretation).join(Scale).filter(Scale.testId == test_id).all()
    if not interpretations:
        raise HTTPException(status_code=404, detail="No interpretations found for this test")
    return interpretations

def batch_create_interpretations(interpretations: List[InterpretationSchema], db: Session):
    """
    Create multiple interpretations in the database.
    """
    db_interpretations = [Interpretation(**interpretation.dict()) for interpretation in interpretations]
    db.add_all(db_interpretations)
    db.commit()
    return db_interpretations

# смущает. если интерпретаций стало после обновления меньше, чем было, то как это обработать?
# а если стало больше, то как их добавить?
def batch_update_interpretations(interpretations: List[InterpretationSchema], db: Session):
    """
    Handle batch update, insert, or delete for interpretations based on incoming data.
    """
    for incoming in interpretations:
        if incoming.id:
            # Поиск существующей интерпретации
            existing = db.query(Interpretation).filter(Interpretation.id == incoming.id).first()

            if not existing:
                raise HTTPException(status_code=404, detail=f"Interpretation with id {incoming.id} not found")

            if not incoming.text.strip():
                # Если текст пуст — удаляем
                db.delete(existing)
            else:
                # Иначе обновляем
                existing.text = incoming.text
        else:
            # Если ID нет и текст НЕ пустой — создаём новую
            if incoming.text.strip():
                new_interp = Interpretation(
                    scaleId=incoming.scaleId,
                    level=incoming.level,
                    text=incoming.text
                )
                db.add(new_interp)
            # Если ID нет и текст пуст — ничего не делаем

    db.commit()
    return {"detail": "Batch upsert complete"}

def delete_interpretation(interpretation_id: int, db: Session):
    """
    Delete an interpretation by its ID.
    """
    db_interpretation = db.query(Interpretation).filter(Interpretation.id == interpretation_id).first()
    if not db_interpretation:
        raise HTTPException(status_code=404, detail=f"Interpretation with id {interpretation_id} not found")
    
    db.delete(db_interpretation)
    db.commit()
    return {"detail": "Interpretation deleted successfully"}

def add_interpretation(interpretation: InterpretationSchema, db: Session):
    """
    Add a new interpretation to the database.
    """
    db_interpretation = Interpretation(**interpretation.dict())
    db.add(db_interpretation)
    db.commit()
    return db_interpretation