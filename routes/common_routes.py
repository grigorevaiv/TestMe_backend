from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db

from models.state_model import StateSchema
from controllers.common_controller import update_state_step

common_routes = APIRouter()

@common_routes.put("/{test_id}/states")
def updateState(test_id: int, state: StateSchema, db: Session = Depends(get_db)):
    return update_state_step(test_id, state, db)