from fastapi import HTTPException
from models.tag_model import Tag
from models.tag_test_model import TagTest
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

#from collections import defaultdict
#from typing import List

from models.test_model import Test
from models.state_model import State

def create_test(test: Test, db: Session):
    existing_test = db.query(Test).filter(Test.title == test.title).first()
    if existing_test:
        raise HTTPException(status_code=400, detail="Test with this title already exists")

    new_test = Test(
        title=test.title,
        description=test.description,
        instructions=test.instructions,
        author=test.author if test.author else None,
        version=test.version if test.version else None
    )

    db.add(new_test)
    db.commit()
    db.refresh(new_test)

    # 1. Создаем состояние
    initial_status = State(
        testId=new_test.id,
        state='draft',
        currentStep=1
    )
    db.add(initial_status)
    db.commit()
    db.refresh(initial_status)

    # 2. Нормализуем и убираем дубли
    normalized_tags = set(tag.strip().lower() for tag in test.tags or [])

    for tag_name in normalized_tags:
        tag = db.query(Tag).filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)

        # Проверка связки
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


def get_all_tests(db: Session):
    tests = db.query(Test).options(joinedload(Test.state)).all()
    if not tests:
        raise HTTPException(status_code=404, detail="No tests found")
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

    # Обновление основных полей
    existing_test.title = test.title
    existing_test.description = test.description
    existing_test.instructions = test.instructions
    existing_test.author = test.author if test.author else None
    existing_test.version = test.version if test.version else None

    # Очистка старых связей тегов
    existing_test.tag_tests.clear()
    db.commit()  # <-- фикс: коммитим удаление связей

    # Добавление новых тегов
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
