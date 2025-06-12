from fastapi import Depends, HTTPException
from auth.check_admin import get_current_admin
from models.admin_model import Admin
from models.tag_model import Tag
from models.tag_test_model import TagTest
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

#from collections import defaultdict
#from typing import List

from models.test_model import Test
from models.state_model import State

def create_test(test: Test, db: Session, current_admin: Admin):
    existing_test = db.query(Test).filter(
        Test.title == test.title,
        Test.admin_id == current_admin.id
        ).first()
    if existing_test:
        raise HTTPException(status_code=400, detail="Test with this title already exists")

    new_test = Test(
        title=test.title,
        description=test.description,
        instructions=test.instructions,
        author=test.author if test.author else None,
        version=test.version if test.version else None,
        admin_id=current_admin.id
    )

    db.add(new_test)
    db.commit()
    db.refresh(new_test)

    initial_status = State(
        testId=new_test.id,
        state='draft',
        currentStep=1
    )
    db.add(initial_status)
    db.commit()
    db.refresh(initial_status)

    normalized_tags = set(tag.strip().lower() for tag in test.tags or [])

    for tag_name in normalized_tags:
        tag = db.query(Tag).filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)

        existing_link = db.query(TagTest).filter_by(test_id=new_test.id, tag_id=tag.id).first()
        if not existing_link:
            tag_test = TagTest(test_id=new_test.id, tag_id=tag.id)
            db.add(tag_test)

    db.commit()

    test_with_state = db.query(Test).options(joinedload(Test.state)).filter(Test.id == new_test.id).first()

    return test_with_state



def get_test(test_id: int, db: Session):
    test = (
        db.query(Test)
        .filter(Test.id == test_id)
        .options(
            joinedload(Test.state),
            joinedload(Test.tag_tests).joinedload(TagTest.tag)
        )
        .first()
    )
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    tags = [tag_test.tag.name for tag_test in test.tag_tests]

    return {
        "id": test.id,
        "title": test.title,
        "author": test.author,
        "version": test.version,
        "description": test.description,
        "instructions": test.instructions,
        "state": test.state,
        "tags": tags
    }


def get_all_tests(db: Session, current_admin: Admin):
    tests = (
        db.query(Test)
        .filter(Test.admin_id == current_admin.id)
        .options(
            joinedload(Test.state),
            joinedload(Test.tag_tests).joinedload(TagTest.tag)
        )
        .order_by(Test.id.asc())
        .all()
    )

    if not tests:
        raise HTTPException(status_code=404, detail="No tests found")

    for test in tests:
        test.tags = [tt.tag.name for tt in test.tag_tests if tt.tag]

    return tests



def update_test(test_id: int, test: Test, db: Session):
    existing_test = (
        db.query(Test)
        .filter(Test.id == test_id)
        .options(joinedload(Test.state), joinedload(Test.tag_tests))
        .first()
    )

    if not existing_test:
        raise HTTPException(status_code=404, detail="Test not found")

    existing_test.title = test.title
    existing_test.description = test.description
    existing_test.instructions = test.instructions
    existing_test.author = test.author if test.author else None
    existing_test.version = test.version if test.version else None

    existing_test.tag_tests.clear()
    db.commit() 

    normalized_tags = set(tag.strip().lower() for tag in test.tags or [])

    for tag_name in normalized_tags:
        tag = db.query(Tag).filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)

        tag_test = TagTest(test_id=test_id, tag_id=tag.id)
        db.add(tag_test)

    db.commit()
    db.refresh(existing_test)

    return existing_test
