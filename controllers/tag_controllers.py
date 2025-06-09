from fastapi import HTTPException
from models.tag_test_model import TagTest
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from models.tag_model import Tag, TagSchema

def create_tag(tag: TagSchema, db: Session):
    existing_tag = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag with this name already exists")
    
    new_tag = Tag(name=tag.name)
    
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    
    return new_tag

def get_all_tags(db: Session):
    tags = (
        db.query(Tag)
        .join(TagTest, Tag.id == TagTest.tag_id)
        .distinct()
        .all()
    )

    if not tags:
        raise HTTPException(status_code=404, detail="No tags found")

    return tags