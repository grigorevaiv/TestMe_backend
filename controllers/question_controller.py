import shutil
import os
from typing import List
from uuid import uuid4

from fastapi import Form, HTTPException, UploadFile, File, Request, Body
from models.tag_test_model import TagTest
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload, join

from models.answer_model import Answer
from models.block_model import Block
from models.question_model import Question, QuestionSchema
from models.test_model import Test


def get_all_questions(db: Session):
    questions = (
        db.query(Question)
        .options(
            joinedload(Question.block)
            .joinedload(Block.test)
            .joinedload(Test.tag_tests)
            .joinedload(TagTest.tag)
        )
        .all()
    )

    result = []
    for q in questions:
        test = q.block.test
        tags = [tt.tag.id for tt in test.tag_tests]
        result.append({
            "id": q.id,
            "text": q.text,
            "imageUrl": q.imageUrl,
            "isActive": q.isActive,
            "blockId": q.blockId,
            "tagsIds": tags,
        })
    return result

def upload_temp_image(
    db: Session,
    file: UploadFile = File(...),
    test_id: int = Form(...)
):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    test_title = test.title
    dir_name = f"{test_id}_{test_title.replace(' ', '_').replace("'", '')}"
    img_path = os.path.join("static", "tmp", dir_name)
    os.makedirs(img_path, exist_ok=True)

    ext = file.filename.split('.')[-1]
    filename = f"{uuid4().hex}.{ext}"
    temp_path = os.path.join(img_path, filename)

    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    public_url = f"/static/tmp/{dir_name}/{filename}".replace("\\", "/")

    return {"imageUrl": public_url}

import re

def sanitize_filename(name: str) -> str:
    # Удаляем запрещённые символы Windows и Unix
    return re.sub(r'[<>:"/\\|?*]', '_', name)


def create_questions(
    request: Request,
    test_id: int,
    questions: List[QuestionSchema],
    db: Session
):
    # 1. Получаем тест
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    # 2. Подготавливаем имя и путь к папке
    safe_title = sanitize_filename(test.title.replace(" ", "_").replace("'", ""))
    dir_name = f"{test_id}_{safe_title}"
    dir_path = os.path.join("static", dir_name)
    tmp_dir_path = os.path.join("static", "tmp", dir_name)

    # 3. Проверяем, есть ли картинки для перемещения
    has_images = any(q.imageUrl and "tmp/" in q.imageUrl for q in questions)

    if has_images:
        os.makedirs(dir_path, exist_ok=True)

    # 4. Создаём вопросы
    for q in questions:
        if q.imageUrl and "tmp/" in q.imageUrl:
            filename = q.imageUrl.split("/")[-1]
            src = os.path.join(tmp_dir_path, filename)
            dst = os.path.join(dir_path, filename)

            if os.path.exists(src):
                shutil.move(src, dst)
                public_path = f"/static/{dir_name}/{filename}"
                q.imageUrl = str(request.base_url).rstrip("/") + public_path
            else:
                print(f"[!] Temporary image not found: {src}")

        new_question = Question(**q.dict())
        db.add(new_question)

    db.commit()

    return {"status": "created", "count": len(questions)}

def sanitize_filename(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', name)


def update_questions(
    request: Request,
    test_id: int,
    questions: List[QuestionSchema],
    db: Session
):
    # 1. Проверка на существование теста
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    # 2. Генерация безопасного пути
    safe_title = sanitize_filename(test.title.replace(" ", "_").replace("'", ""))
    dir_name = f"{test_id}_{safe_title}"
    dir_path = os.path.join("static", dir_name)
    tmp_dir_path = os.path.join("static", "tmp", dir_name)

    # 3. Проверка на наличие картинок для перемещения
    has_images = any(q.imageUrl and "tmp/" in q.imageUrl for q in questions)
    if has_images:
        os.makedirs(dir_path, exist_ok=True)

    updated_count = 0

    # 4. Обновление вопросов
    for q in questions:
        if not q.id:
            raise HTTPException(status_code=400, detail="Missing ID for update")

        existing = db.query(Question).filter(Question.id == q.id).first()
        if not existing:
            raise HTTPException(status_code=404, detail=f"Question with ID {q.id} not found")

        # Перемещение картинки, если нужно
        if q.imageUrl and "tmp/" in q.imageUrl:
            filename = q.imageUrl.split("/")[-1]
            src = os.path.join(tmp_dir_path, filename)
            dst = os.path.join(dir_path, filename)

            if os.path.exists(src):
                shutil.move(src, dst)
                public_path = f"/static/{dir_name}/{filename}"
                q.imageUrl = str(request.base_url).rstrip("/") + public_path
            else:
                print(f"[!] Temporary image not found: {src}")

        # Обновление полей
        for key, value in q.dict(exclude_unset=True).items():
            setattr(existing, key, value)

        updated_count += 1

    db.commit()

    return {"status": "updated", "count": updated_count}


class DeleteImagePayload(BaseModel):
    imageUrl: str

def delete_image(payload: DeleteImagePayload, db: Session):
    relative_path = payload.imageUrl.lstrip("/")
    file_path = os.path.join(os.getcwd(), relative_path)

    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

    question = db.query(Question).filter(Question.id == payload.questionId).first()
    if question:
        question.imageUrl = None
        db.commit()

    return {"status": "deleted"}


def get_questions_by_test(test_id: int, db: Session):
    block_ids_subquery = (
        db.query(Block.id)
        .filter(Block.testId == test_id)
        .subquery()
    )

    questions = (
        db.query(Question)
        .filter(Question.blockId.in_(block_ids_subquery))
        .order_by(Question.id)
        .all()
    )

    return questions

def delete_question(question_id: int, db: Session):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    db.delete(question)
    db.commit()

    return {"status": "deleted", "questionId": question_id}