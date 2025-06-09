from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

#from collections import defaultdict
#from typing import List

from models.test_model import Test
from models.block_model import Block
from models.scale_model import Scale


def create_scale(scale: Scale, db: Session):
    new_scale = Scale(
        pole1=scale.pole1,
        pole2=scale.pole2 if scale.pole2 else None,
        testId=scale.testId,
        blockId=scale.blockId,
        scaleType=scale.scaleType
    )
    
    db.add(new_scale)
    db.commit()
    db.refresh(new_scale)
    
    return new_scale

def create_scales_batch(scales: List[Scale], db: Session):
    created_scales = []
    for scale in scales:
        new_scale = Scale(
            pole1=scale.pole1,
            pole2=scale.pole2 if scale.pole2 else None,
            testId=scale.testId,
            blockId=scale.blockId,
            scaleType=scale.scaleType
        )
        db.add(new_scale)
        created_scales.append(new_scale)
    
    db.commit()  # Один раз после всех добавлений
    return created_scales

def get_scales_by_test_id(test_id: int, db: Session):
    scales = db.query(Scale).filter(Scale.testId == test_id).order_by(Scale.id).all()
    if not scales:
        raise HTTPException(status_code=404, detail="No scales found for this test")
    
    return scales

def update_scale(scale_id: int, scale_data: Scale, db: Session):
    scale = db.query(Scale).filter(Scale.id == scale_id).first()
    if not scale:
        raise HTTPException(status_code=404, detail="Scale not found")
    scale.scaleType = scale_data.scaleType
    scale.pole1 = scale_data.pole1
    scale.pole2 = scale_data.pole2
    scale.blockId = scale_data.blockId
    scale.testId = scale_data.testId
    scale.scaleType = scale_data.scaleType

    db.commit()
    db.refresh(scale)
    return scale


def delete_scale(scale_id: int, db: Session):
    scale = db.query(Scale).filter(Scale.id == scale_id).first()
    if not scale:
        raise HTTPException(status_code=404, detail="Scale not found")

    db.delete(scale)
    db.commit()
    return {"message": f"Scale {scale_id} successfully deleted"}
