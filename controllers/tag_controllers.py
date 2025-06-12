from fastapi import HTTPException
from models.admin_model import Admin
from models.tag_test_model import TagTest
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from models.tag_model import Tag, TagSchema
from models.test_model import Test
from models.tag_test_model import TagTest

def create_tag(tag: TagSchema, db: Session):
    existing_tag = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag with this name already exists")
    
    new_tag = Tag(name=tag.name)
    
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    
    return new_tag

def get_all_tags(db: Session, current_admin: Admin):
    tags = (
        db.query(Tag)
        .join(TagTest, Tag.id == TagTest.tag_id)
        .join(Test, Test.id == TagTest.test_id)
        .filter(Test.admin_id == current_admin.id)
        .distinct()
        .all()
    )
    return tags

def get_suggested_tags(db: Session, current_admin: Admin):
    tags = (
        db.query(Tag.name)
        .join(TagTest, Tag.id == TagTest.tag_id)
        .join(Test, Test.id == TagTest.test_id)
        .filter(Test.admin_id == current_admin.id)
        .distinct()
        .all()
    )
    return [t[0] for t in tags]