from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db

from models.scale_model import ScaleSchema
from controllers.scale_controller import (
    create_scale,
    get_scales_by_test_id,
    update_scale,
    delete_scale,
    create_scales_batch
)

scale_routes = APIRouter()

@scale_routes.post("/{test_id}/scales")
def createScale(scale: ScaleSchema, db: Session = Depends(get_db)):
    return create_scale(scale, db)

@scale_routes.post("/{test_id}/scales/batch")
def createScalesBatch(test_id: int, scales: List[ScaleSchema], db: Session = Depends(get_db)):
    if not scales:
        raise HTTPException(status_code=400, detail="No scales provided for batch creation")
    
    return create_scales_batch(scales, db)

@scale_routes.get("/{test_id}/scales")
def getScales(test_id: int, db: Session = Depends(get_db)):
    return get_scales_by_test_id(test_id, db)

@scale_routes.put("/scales/{scale_id}")
def updateScale(scale_id: int, scale: ScaleSchema, db: Session = Depends(get_db)):
    return update_scale(scale_id, scale, db)

@scale_routes.delete("/scales/{scale_id}")
def deleteScale(scale_id: int, db: Session = Depends(get_db)):
    return delete_scale(scale_id, db)
