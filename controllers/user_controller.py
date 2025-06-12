from typing import List
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from auth.check_admin import get_current_admin
from models.admin_model import Admin
from models.user_model import User, UserSchema

def create_user(user: User, db: Session, current_admin: Admin):
    
    new_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        birth_date=user.birth_date,
        is_active=user.is_active,
        assigned_to_admin=current_admin.id
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

def get_users(db: Session, current_admin: Admin):
    users = db.query(User).filter(User.assigned_to_admin == current_admin.id).order_by(User.id.asc()).all()
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
    
    for key, value in user_data.model_dump(exclude={'id', 'assigned_to_admin'}).items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    
    return UserSchema.model_validate(user)