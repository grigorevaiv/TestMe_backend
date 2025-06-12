from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from auth.check_admin import get_current_admin
from database.database import get_db
from models.admin_model import Admin
from models.tag_model import TagSchema

from controllers.tag_controllers import create_tag, get_all_tags, get_suggested_tags
tag_routes = APIRouter(dependencies=[Depends(get_current_admin)])

@tag_routes.post("/tags")
def createTag(tag: TagSchema, db: Session = Depends(get_db)):
    return create_tag(tag, db)

@tag_routes.get("/tags/all")
def getAllTags(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """
    Retrieve all tags associated with the current admin.
    """
    try:
        return get_all_tags(db, current_admin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@tag_routes.get("/tags/suggested")
def getSuggestedTags(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """
    Retrieve suggested tags based on a search query.
    """
    try:
        return get_suggested_tags(db, current_admin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))