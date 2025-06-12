from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, Request, Body
from auth.check_admin import get_current_admin
from database.database import get_db
from sqlalchemy.orm import Session
from models.admin_model import Admin
from models.user_model import User, UserSchema
from controllers.user_controller import create_user, get_users, get_user_by_id, update_user
user_routes = APIRouter(dependencies=[Depends(get_current_admin)])
@user_routes.post("")
def createNewUser(user: UserSchema, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """
    Create a new user.
    """
    new_user = create_user(user, db, current_admin)
    return new_user

@user_routes.get("")
def getAllUsers(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """
    Get all users.
    """
    users = get_users(db, current_admin)
    return users

@user_routes.get("/{user_id}")
def getUserById(user_id: int, db: Session = Depends(get_db)):
    """
    Get a user by ID.
    """
    user = get_user_by_id(user_id, db)
    return user

@user_routes.put("/{user_id}")
def updateUser(user_id: int, user_data: UserSchema, db: Session = Depends(get_db)):
    """
    Update a user by ID.
    """
    updated_user = update_user(user_id, user_data, db)
    return updated_user

@user_routes.patch("/{user_id}/deactivate")
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    db.commit()
    return {"message": "Patient deactivated successfully"}

@user_routes.patch("/{user_id}/reactivate")
def reactivate_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    db.commit()
    return {"message": "Patient reactivated successfully"}
