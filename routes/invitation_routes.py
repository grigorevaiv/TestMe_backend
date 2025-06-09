from datetime import datetime
from fastapi import APIRouter, Body, HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db

from models.invitation_model import Invitation, InvitationSchema, CreateInvitationSchema
from controllers.invitation_controller import create_test_invitation
from models.user_model import User
invitation_routes = APIRouter()

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

    # Найдём инвайт по токену
    invitation = db.query(Invitation).filter(
        Invitation.token == token,
        Invitation.expires_at > datetime.utcnow(),
        Invitation.used == False
    ).first()

    if not invitation:
        raise HTTPException(status_code=404, detail="Invalid or expired invitation")

    # Найдём пользователя по user_id из инвайта
    user = db.query(User).filter(User.id == invitation.user_id).first()

    if not user or user.email.lower() != email.lower():
        raise HTTPException(status_code=400, detail="Email does not match the invited user")

    return {
        "userId": user.id,
        "testId": invitation.test_id,
        "email": user.email,
        "firstName": user.first_name,
        "lastName": user.last_name
    }
