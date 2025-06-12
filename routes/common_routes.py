from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db

from models.state_model import StateSchema
from controllers.common_controller import update_state_step
from auth.check_admin import get_current_admin

common_routes = APIRouter(dependencies=[Depends(get_current_admin)])

@common_routes.put("/{test_id}/states")
def updateState(test_id: int, state: StateSchema, db: Session = Depends(get_db)):
    return update_state_step(test_id, state, db)