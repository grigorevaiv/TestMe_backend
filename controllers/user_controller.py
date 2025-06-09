from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.user_model import User, UserSchema

def create_user(user: User, db: Session):
    
    new_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        assigned_to_admin=user.assigned_to_admin
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

def get_users(db: Session):
    users = db.query(User).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    
    return [UserSchema.model_validate(u) for u in users]

def get_user_by_id(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserSchema.model_validate(user)

def update_user(user_id: int, user_data: UserSchema, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user_data.model_dump(exclude={'id'}).items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    
    return UserSchema.model_validate(user)