from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, Request, Body
from database.database import get_db
from sqlalchemy.orm import Session
from models.user_model import User, UserSchema
from controllers.user_controller import create_user, get_users, get_user_by_id, update_user
user_routes = APIRouter()
@user_routes.post("")
def createNewUser(user: UserSchema, db: Session = Depends(get_db)):
    """
    Create a new user.
    """
    new_user = create_user(user, db)
    return new_user

@user_routes.get("")
def getAllUsers(db: Session = Depends(get_db)):
    """
    Get all users.
    """
    users = get_users(db)
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