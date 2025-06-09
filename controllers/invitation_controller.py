# ⛓ core.py

import os
from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta
from models.invitation_model import Invitation
from models.user_model import User
from dotenv import load_dotenv
load_dotenv()


INVITE_LINK_BASE_URL = os.getenv("INVITE_LINK_BASE_URL")

def create_test_invitation(user_email: str, user_id: int, test_id: int, db: Session):
    existing = db.query(Invitation).filter(
        Invitation.user_id == user_id,
        Invitation.test_id == test_id,
        Invitation.used == False,
        Invitation.expires_at > datetime.utcnow()
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="An active invitation already exists for this user and test."
        )
    
    token = str(uuid4())
    expires_at = datetime.utcnow() + timedelta(days=3)

    invitation = Invitation(
        token=token,
        user_id=user_id,
        test_id=test_id,
        expires_at=expires_at
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    link = f"{INVITE_LINK_BASE_URL}/{token}/verify"

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        send_invite_email(
            to_email=user_email,
            to_name=f"{user.first_name} {user.last_name}",
            invite_link=link
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error sending invite: {str(e)}")

    return invitation


import os
from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from sib_api_v3_sdk.models import SendSmtpEmail

load_dotenv()

INVITE_API_KEY = os.getenv("INVITE_API_KEY")

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = INVITE_API_KEY

def send_invite_email(to_email: str, to_name: str, invite_link: str):
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    send_smtp_email = SendSmtpEmail(
        to=[{"email": to_email, "name": to_name}],
        sender={"name": "TestMe", "email": "joezefin@gmail.com"},
        subject="You've been invited to take a test",
        html_content=f"""
            <p>Dear {to_name},</p>
            <p>Your doctor has assigned you a test. To take it, please click the link below:</p>
            <p><a href="{invite_link}">{invite_link}</a></p>
            <p>This link will expire in 3 days.</p>
        """
    )

    try:
        response = api_instance.send_transac_email(send_smtp_email)
        print("Email sent. Message ID:", response.message_id)
        return response
    except ApiException as e:
        print("Error sending email via Brevo:", e)
        raise
