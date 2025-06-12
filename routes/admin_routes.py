from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth.check_admin import create_access_token, verify_password, get_current_admin, hash_password
from database.database import get_db
from models.admin_model import Admin, AdminLoginSchema, AdminSchema
from typing import List

admin_router = APIRouter()


@admin_router.get("/", response_model=List[AdminSchema])
def get_all_admins(db: Session = Depends(get_db)):
    return db.query(Admin).all()


@admin_router.get("/{admin_id}", response_model=AdminSchema)
def get_admin_by_id(admin_id: int, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin

@admin_router.post("/login")
def login_admin(
    credentials: AdminLoginSchema,
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == credentials.email).first()
    if not admin or not verify_password(credentials.password, admin.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={
        "sub": str(admin.id),
        "first_name": admin.first_name,
        "last_name": admin.last_name
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "admin": {
            "id": admin.id,
            "firstName": admin.first_name,
            "lastName": admin.last_name
        }
    }

@admin_router.post("/", response_model=AdminSchema)
def create_admin(admin: AdminSchema, db: Session = Depends(get_db)):
    existing = db.query(Admin).filter(Admin.email == admin.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin with this email already exists")
    
    new_admin = Admin(
        first_name=admin.first_name,
        last_name=admin.last_name,
        email=admin.email,
        password=hash_password(admin.password)
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin