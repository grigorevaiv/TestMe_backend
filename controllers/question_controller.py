import shutil
import os
from typing import List
from uuid import uuid4
from dotenv import load_dotenv
import requests
from supabase import create_client, Client
from fastapi import Form, HTTPException, UploadFile, File, Request, Body
from models.tag_test_model import TagTest
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload, join

from models.answer_model import Answer
from models.block_model import Block
from models.question_model import Question, QuestionSchema
from models.test_model import Test
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
            "testTitle": test.title,
        })
    return result
'''
def upload_temp_image(
    db: Session,
    file: UploadFile = File(...),
    test_id: int = Form(...)
):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    dir_name = build_test_dir_name(test.id, test.title)
    img_path = os.path.join("static", "tmp", dir_name)
    os.makedirs(img_path, exist_ok=True)

    ext = file.filename.split('.')[-1]
    filename = f"{uuid4().hex}.{ext}"
    temp_path = os.path.join(img_path, filename)
    print(f"[UPLOAD] Saving temp file to: {temp_path}")
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    public_url = f"/static/tmp/{dir_name}/{filename}".replace("\\", "/")

    return {"imageUrl": public_url}
'''
import re

def sanitize_filename(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def build_test_dir_name(test_id: int, title: str) -> str:
    clean = title.strip().replace(" ", "_").replace("'", "")
    clean = sanitize_filename(clean)
    clean = re.sub(r'_+', '_', clean)
    return f"{test_id}_{clean}"
'''
def create_questions(
    request: Request,
    test_id: int,
    questions: List[QuestionSchema],
    db: Session
):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    dir_name = build_test_dir_name(test.id, test.title)
    dir_path = os.path.join("static", dir_name)
    tmp_dir_path = os.path.join("static", "tmp", dir_name)

    os.makedirs(dir_path, exist_ok=True)

    for q in questions:
        if q.imageUrl and "tmp/" in q.imageUrl:
            filename = q.imageUrl.split("/")[-1]
            src = os.path.abspath(os.path.join(tmp_dir_path, filename))
            dst = os.path.abspath(os.path.join(dir_path, filename))
            print(f"[ABS PATH] src = {src}")
            print(f"[ABS PATH] dst = {dst}")
            print(f"[DEBUG] Checking if file exists: {src}")
            print(f"[DEBUG] Exists? {os.path.exists(src)}")
            if os.path.exists(src):
                print(f"Moving image from {src} to {dst}")
                shutil.move(src, dst)
                public_path = f"/static/{dir_name}/{filename}"
                q.imageUrl = str(request.base_url).rstrip("/") + public_path
            else:
                print(f"[!] Temporary image not found: {src}")

        new_question = Question(**q.dict())
        db.add(new_question)

    db.commit()

    return {"status": "created", "count": len(questions)}

def update_questions(
    request: Request,
    test_id: int,
    questions: List[QuestionSchema],
    db: Session
):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    dir_name = build_test_dir_name(test.id, test.title)
    dir_path = os.path.join("static", dir_name)
    tmp_dir_path = os.path.join("static", "tmp", dir_name)

    os.makedirs(dir_path, exist_ok=True)

    updated_count = 0

    for q in questions:
        if not q.id:
            raise HTTPException(status_code=400, detail="Missing ID for update")

        existing = db.query(Question).filter(Question.id == q.id).first()
        if not existing:
            raise HTTPException(status_code=404, detail=f"Question with ID {q.id} not found")

        if q.imageUrl and "tmp/" in q.imageUrl:
            filename = q.imageUrl.split("/")[-1]
            src = os.path.abspath(os.path.join(tmp_dir_path, filename))
            dst = os.path.abspath(os.path.join(dir_path, filename))
            print(f"[ABS PATH] src = {src}")
            print(f"[ABS PATH] dst = {dst}")
            print(f"[DEBUG] Checking if file exists: {src}")
            print(f"[DEBUG] Exists? {os.path.exists(src)}")
            if os.path.exists(src):
                print(f"Moving image from {src} to {dst}")
                shutil.move(src, dst)
                public_path = f"/static/{dir_name}/{filename}"
                q.imageUrl = str(request.base_url).rstrip("/") + public_path
            else:
                print(f"[!] Temporary image not found: {src}")

        for key, value in q.dict(exclude_unset=True).items():
            setattr(existing, key, value)

        updated_count += 1

    db.commit()

    return {"status": "updated", "count": updated_count}
'''

def upload_temp_image(
    db: Session,
    file: UploadFile = File(...),
    test_id: int = Form(...)
):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    ext = file.filename.split('.')[-1]
    filename = f"{uuid4().hex}.{ext}"
    folder = build_test_dir_name(test.id, test.title)
    path_in_bucket = f"{folder}/{filename}"

    try:
        content = file.file.read()
        res = supabase.storage.from_(SUPABASE_BUCKET).upload(
            path_in_bucket,
            content,
            {"content-type": file.content_type, "upsert": True}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase upload error: {e}")

    public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(path_in_bucket)

    return {"imageUrl": public_url}

def create_questions(
    test_id: int,
    questions: List[QuestionSchema],
    db: Session
):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    for q in questions:
        new_question = Question(**q.dict())
        db.add(new_question)

    db.commit()
    return {"status": "created", "count": len(questions)}

def update_questions(
    test_id: int,
    questions: List[QuestionSchema],
    db: Session
):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    updated_count = 0

    for q in questions:
        if not q.id:
            raise HTTPException(status_code=400, detail="Missing ID for update")

        existing = db.query(Question).filter(Question.id == q.id).first()
        if not existing:
            raise HTTPException(status_code=404, detail=f"Question with ID {q.id} not found")

        for key, value in q.dict(exclude_unset=True).items():
            setattr(existing, key, value)

        updated_count += 1

    db.commit()
    return {"status": "updated", "count": updated_count}



class DeleteImagePayload(BaseModel):
    imageUrl: str

from urllib.parse import urlparse

def delete_image(payload: DeleteImagePayload, db: Session):
    image_url = payload.imageUrl
    if not image_url:
        raise HTTPException(status_code=400, detail="No image URL provided")
    parsed = urlparse(image_url)
    object_path = parsed.path.split(f'/object/public/{SUPABASE_BUCKET}/')[-1]
    delete_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/remove"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(delete_url, headers=headers, json={
        "prefixes": [object_path]
    })

    if response.status_code != 200:
        raise HTTPException(500, detail=f"Failed to delete from Supabase: {response.text}")

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