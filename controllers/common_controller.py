from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.state_model import State

def update_state_step(test_id: int, state: State, db: Session):
    existing_state = db.query(State).filter(State.testId == test_id).first()
    print(existing_state)
    if not existing_state:
        raise HTTPException(status_code=404, detail="State not found")
    existing_state.state = state.state
    existing_state.currentStep = state.currentStep
    db.commit()
    db.refresh(existing_state)
    
    return existing_state