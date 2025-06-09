from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, Request, Body
from database.database import get_db
from models.tag_test_model import TagTest
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload, join

from models.weight_model import Weight, WeightSchema
from controllers.weights_controller import create_weights, update_weights, get_all_weights

weight_routes = APIRouter()
@weight_routes.get("/{test_id}/weights")
def get_weights(test_id: int, db: Session = Depends(get_db)):
    """
    Get all weights for a specific test.
    """
    weights = get_all_weights(test_id, db)
    return weights

@weight_routes.post("/weights/batch")
def batch_create_weights(weights: list[WeightSchema], db: Session = Depends(get_db)):
    """
    Batch create weights for answers.
    """
    if not weights:
        raise HTTPException(status_code=400, detail="No weights provided for batch creation.")
    
    create_weights(db, weights)
    return {"message": "Weights created successfully"}

@weight_routes.put("/weights/batch")
def batch_update_weights(weights: list[WeightSchema], db: Session = Depends(get_db)):
    """
    Batch update weights for answers.
    """
    if not weights:
        raise HTTPException(status_code=400, detail="No weights provided for batch update.")
    
    update_weights(db, weights)
    return {"message": "Weights updated successfully"}