from models.interpretation_model import InterpretationSchema
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from controllers.interpretation_controller import (
    get_test_interpretations,
    batch_create_interpretations,
    batch_update_interpretations,
    delete_interpretation,
    add_interpretation
)
from auth.check_admin import get_current_admin


interpretation_routes = APIRouter(dependencies=[Depends(get_current_admin)])

@interpretation_routes.get("/{test_id}/interpretations")
def getTestInterpretations(test_id: int, db: Session = Depends(get_db)):
    """
    Get all interpretations for a specific test.
    """
    interpretations = get_test_interpretations(test_id, db)
    return interpretations

@interpretation_routes.post("/batch/interpretations")
def batchAddInterpretations(interpretations: List[InterpretationSchema], db: Session = Depends(get_db)):
    """
    Create multiple interpretations.
    """
    if not interpretations:
        raise HTTPException(status_code=400, detail="No interpretations provided")
    created_interpretations = batch_create_interpretations(interpretations, db)
    return created_interpretations

@interpretation_routes.put("/batch/interpretations")
def batchUpdateInterpretations(interpretations: List[InterpretationSchema], db: Session = Depends(get_db)):
    """
    Update, insert, or delete interpretations in batch.
    """
    if not interpretations:
        raise HTTPException(status_code=400, detail="No interpretations provided")
    result = batch_update_interpretations(interpretations, db)
    return result

