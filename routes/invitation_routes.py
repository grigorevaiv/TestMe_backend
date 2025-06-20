from datetime import datetime
from fastapi import APIRouter, Body, HTTPException, Depends
from sqlalchemy.orm import Session
from auth.check_admin import get_current_admin
from database.database import get_db

from models.admin_model import Admin
from models.invitation_model import Invitation, InvitationSchema, CreateInvitationSchema
from controllers.invitation_controller import create_test_invitation
from models.test_model import Test
from models.user_model import User
invitation_routes = APIRouter(dependencies=[Depends(get_current_admin)])

@invitation_routes.post("/invitations")
def createInvitation(
    invitation: CreateInvitationSchema, db: Session = Depends(get_db)
):
    new_invitation = create_test_invitation(
        user_email=invitation.user_email,
        user_id=invitation.user_id,
        test_id=invitation.test_id,
        db=db
    )
    return new_invitation

@invitation_routes.post("/invitations/verify")
def verify_invitation(
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    token = data.get("token")
    email = data.get("email")

    if not token or not email:
        raise HTTPException(status_code=400, detail="Token and email are required")

    invitation = db.query(Invitation).filter(
        Invitation.token == token,
        Invitation.expires_at > datetime.utcnow(),
        Invitation.used == False
    ).first()

    if not invitation:
        raise HTTPException(status_code=404, detail="Invalid or expired invitation")

    user = db.query(User).filter(User.id == invitation.user_id).first()

    if not user or user.email.lower() != email.lower():
        raise HTTPException(status_code=400, detail="Email does not match the invited user")

    return {
        "userId": user.id,
        "testId": invitation.test_id,
        "token": invitation.token,
        "email": user.email,
        "firstName": user.first_name,
        "lastName": user.last_name
    }

@invitation_routes.get("/token-status/{token}")
def get_token_status(
    token: str, db: Session = Depends(get_db)
):
    invitation = db.query(Invitation).filter(
        Invitation.token == token
    ).first()

    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")

    return {
        "used": invitation.used
    }

@invitation_routes.get("/invitations/{token}")
def get_invitation_info(token: str, db: Session = Depends(get_db)):
    invitation = db.query(Invitation).filter(
        Invitation.token == token,
        Invitation.expires_at > datetime.utcnow()
    ).first()

    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found or expired")

    test = db.query(Test).filter(Test.id == invitation.test_id).first()
    if not test:
        raise HTTPException(status_code=500, detail="Test not found")

    admin = db.query(Admin).filter(Admin.id == test.admin_id).first()
    if not admin:
        raise HTTPException(status_code=500, detail="Admin not found")
    
    user = db.query(User).filter(User.id == invitation.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "userFullName": f"{user.first_name} {user.last_name}",
        "testTitle": test.title,
        "invitedBy": f"{admin.first_name} {admin.last_name}"
    }