from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.norm_model import Norm, NormSchema
from models.scale_model import Scale


def get_test_norms(test_id: int, db: Session):
    norms = (
        db.query(Norm)
        .join(Scale, Norm.scaleId == Scale.id)
        .filter(Scale.testId == test_id)
        .all()
    )
    if not norms:
        raise HTTPException(status_code=404, detail="No norms found for this test")
    return norms

def batch_create_norms(norms: List[NormSchema], db: Session):
    """
    Create multiple norms in the database.
    """
    db_norms = [Norm(**norm.dict()) for norm in norms]
    db.add_all(db_norms)
    db.commit()
    return db_norms

def batch_update_norms(norms: List[NormSchema], db: Session):
    """
    Update multiple norms in the database.
    """
    for norm in norms:
        db_norm = db.query(Norm).filter(Norm.id == norm.id).first()
        if not db_norm:
            raise HTTPException(status_code=404, detail=f"Norm with id {norm.id} not found")

        db_norm.mean = norm.mean
        db_norm.stdDev = norm.stdDev
        db_norm.type = norm.type

    db.commit()
    return norms
