from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from models.tag_model import TagSchema

from controllers.tag_controllers import create_tag, get_all_tags
tag_routes = APIRouter()

@tag_routes.post("/tags")
def createTag(tag: TagSchema, db: Session = Depends(get_db)):
    return create_tag(tag, db)

@tag_routes.get("/tags/all")
def getAllTags(db: Session = Depends(get_db)):
    """
    Retrieve all tags from the database.
    """
    try:
        return get_all_tags(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))